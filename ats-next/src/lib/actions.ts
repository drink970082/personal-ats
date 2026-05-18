'use server'

import { prisma } from '@/lib/db'
import { Prisma } from '@prisma/client'
import { STATUSES } from '@/lib/constants'

export async function getApplications(params: {
    page?: number
    size?: number
    status?: string
    historicalStatus?: string
    category?: string
    search?: string
}) {
    const page = params.page || 0
    const size = params.size || 10
    const status = params.status === 'all' ? undefined : params.status
    const historicalStatus = params.historicalStatus === 'all' ? undefined : params.historicalStatus
    const category = params.category === 'all' ? undefined : params.category
    const search = params.search || ''

    const where: Prisma.applicationsWhereInput = {
        AND: [
            status ? { status } : {},
            historicalStatus ? { status_history: { some: { status: historicalStatus } } } : {},
            category ? { category } : {},
            search
                ? {
                    OR: [
                        { company_name: { contains: search } },
                        { job_title: { contains: search } },
                    ],
                }
                : {},
        ],
    }

    const [data, total] = await Promise.all([
        prisma.applications.findMany({
            where,
            skip: page * size,
            take: size,
            orderBy: { date_applied: 'desc' },
        }),
        prisma.applications.count({ where }),
    ])

    return { data, total }
}

export async function addApplication(data: {
    company_name: string
    job_title: string
    date_applied: string
    category?: string
    status?: string
    application_url?: string
    notes?: string
}) {
    try {
        if (!data.company_name || !data.job_title || !data.date_applied) {
            return { success: false, error: 'Missing required fields' }
        }

        const existing = await prisma.applications.findFirst({
            where: {
                company_name: data.company_name,
                job_title: data.job_title,
            },
        })

        if (existing) {
            return {
                success: false,
                error: `Application for ${data.company_name} - ${data.job_title} already exists`,
            }
        }

        const newApp = await prisma.applications.create({
            data: {
                company_name: data.company_name,
                job_title: data.job_title,
                date_applied: data.date_applied,
                category: data.category || 'Others',
                status: data.status || 'Applied',
                application_url: data.application_url || '',
                notes: data.notes || '',
                last_updated: new Date().toISOString(),
            },
        })

        return { success: true, data: newApp }
    } catch (error: any) {
        return { success: false, error: error.message }
    }
}

export async function updateApplicationDetails(
    id: number,
    data: { company_name: string; job_title: string; category: string }
) {
    try {
        await prisma.applications.update({
            where: { id },
            data: {
                company_name: data.company_name,
                job_title: data.job_title,
                category: data.category,
            },
        })
        return { success: true }
    } catch (error: any) {
        return { success: false, error: error.message }
    }
}

export async function updateApplicationStatus(id: number, status: string, date?: string, notes?: string) {
    try {
        if (!STATUSES.includes(status as any)) {
            return { success: false, error: 'Invalid status' }
        }

        const app = await prisma.applications.findUnique({ where: { id } })
        if (!app) {
            return { success: false, error: 'Application not found' }
        }

        if (app.status === status) {
            return { success: false, error: `Application is already in '${status}' status` }
        }

        // Determine timestamp: use provided date (append noon UTC so it doesn't shift days in local timezones) or current time
        const timestamp = date ? new Date(`${date}T12:00:00Z`).toISOString() : new Date().toISOString()

        await prisma.$transaction(async (tx) => {
            await tx.applications.update({
                where: { id },
                data: { status, last_updated: new Date().toISOString() },
            })

            await tx.status_history.create({
                data: {
                    application_id: id,
                    status,
                    timestamp,
                },
            })
        })

        return { success: true }
    } catch (error: any) {
        return { success: false, error: error.message }
    }
}

export async function getKPIs() {
    const apps = await prisma.applications.findMany()

    const stats = {
        applied: 0,   // TOTAL count
        active: 0,
        assessment: 0,
        interviewing: 0,
        rejected: 0,
        offer: 0,
    }

    // "Applied" = total number of applications (per design_pattern.md)
    stats.applied = apps.length

    for (const app of apps) {
        const status = app.status.toLowerCase()
        if (status === 'online assessment') stats.assessment += 1
        else if (status.includes('interviewing')) stats.interviewing += 1
        else if (status === 'rejected') stats.rejected += 1
        else if (status === 'offer') stats.offer += 1
    }

    // Active = Total - Rejected - Offer
    stats.active = apps.length - stats.rejected - stats.offer

    return stats
}

export async function deleteApplication(id: number) {
    try {
        await prisma.applications.delete({
            where: { id },
        })
        return { success: true }
    } catch (error: any) {
        return { success: false, error: error.message }
    }
}

export async function getApplicationHistory(id: number) {
    try {
        const history = await prisma.status_history.findMany({
            where: { application_id: id },
            orderBy: { timestamp: 'desc' },
        })
        return { success: true, data: history }
    } catch (error: any) {
        return { success: false, error: error.message }
    }
}

export async function deleteHistoryItem(id: number) {
    try {
        // Find the history item first to get the application_id
        const item = await prisma.status_history.findUnique({
            where: { id },
            select: { application_id: true }
        })

        if (!item) {
            return { success: false, error: 'History item not found' }
        }

        await prisma.status_history.delete({
            where: { id },
        })

        // Find the most recent history item after deletion
        const latestHistory = await prisma.status_history.findFirst({
            where: { application_id: item.application_id },
            orderBy: { timestamp: 'desc' }
        })

        // Update application status to the most recent history, or 'Applied' if empty
        const newStatus = latestHistory ? latestHistory.status : 'Applied'
        await prisma.applications.update({
            where: { id: item.application_id },
            data: { status: newStatus }
        })

        return { success: true }
    } catch (error: any) {
        return { success: false, error: error.message }
    }
}

export async function getStatusFlow() {
    try {
        const apps = await prisma.applications.findMany({
            include: { status_history: { orderBy: { timestamp: 'asc' } } },
        })

        const transitions: { from: string; to: string }[] = []

        for (const app of apps) {
            const history = app.status_history

            if (history.length === 0) {
                // No history at all — just use current status
                const to = app.status === 'Applied' ? 'No Response' : app.status
                transitions.push({ from: 'Applied', to })
            } else {
                // Build the full chain: start with Applied, then each history entry
                const chain: string[] = ['Applied']
                for (const h of history) {
                    // Avoid duplicate consecutive statuses
                    if (chain[chain.length - 1] !== h.status) {
                        chain.push(h.status)
                    }
                }
                // If current status differs from last history entry, add it
                if (chain[chain.length - 1] !== app.status) {
                    chain.push(app.status === 'Applied' ? 'No Response' : app.status)
                }
                // If chain is just ['Applied'] with no transitions, mark as No Response
                if (chain.length === 1) {
                    transitions.push({ from: 'Applied', to: 'No Response' })
                } else {
                    for (let i = 0; i < chain.length - 1; i++) {
                        transitions.push({ from: chain[i], to: chain[i + 1] })
                    }
                }
            }
        }

        const flowMap = new Map<string, number>()
        for (const t of transitions) {
            const key = `${t.from}|||${t.to}`
            flowMap.set(key, (flowMap.get(key) || 0) + 1)
        }

        const flows = Array.from(flowMap.entries()).map(([key, value]) => {
            const [from, to] = key.split('|||')
            return { from, to, value }
        })

        return { success: true, data: flows }
    } catch (error: any) {
        return { success: false, error: error.message, data: [] }
    }
}

export async function getTimelineData() {
    try {
        const apps = await prisma.applications.findMany({
            select: { date_applied: true },
        })

        const counts = new Map<string, number>()
        for (const app of apps) {
            const date = app.date_applied.split('T')[0]
            counts.set(date, (counts.get(date) || 0) + 1)
        }

        const data = Array.from(counts.entries())
            .map(([date, count]) => ({ date, count }))
            .sort((a, b) => a.date.localeCompare(b.date))

        return { success: true, data }
    } catch (error: any) {
        return { success: false, error: error.message, data: [] }
    }
}

export async function getCategoryData() {
    try {
        const apps = await prisma.applications.findMany({
            select: { category: true },
        })

        const counts = new Map<string, number>()
        for (const app of apps) {
            const cat = app.category || 'Others'
            counts.set(cat, (counts.get(cat) || 0) + 1)
        }

        const data = Array.from(counts.entries())
            .map(([name, value]) => ({ name, value }))
            .sort((a, b) => b.value - a.value)

        return { success: true, data }
    } catch (error: any) {
        return { success: false, error: error.message, data: [] }
    }
}
