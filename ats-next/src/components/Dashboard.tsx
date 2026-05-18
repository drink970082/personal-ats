
'use client'

import { useState } from 'react'
import {
    getApplications,
    addApplication,
    updateApplicationStatus,
    deleteApplication,
    getApplicationHistory,
    getKPIs,
    deleteHistoryItem,
    getStatusFlow,
    getTimelineData,
    getCategoryData,
    updateApplicationDetails,
} from '@/lib/actions'
import { ApplicationTable } from './ApplicationTable'
import { KPIGrid } from './KPIGrid'
import { AddApplicationForm } from './AddApplicationForm'
import { StatusHistoryModal } from './StatusHistoryModal'
import { StatusFunnel } from './StatusFunnel'
import { TimelineHeatmap } from './TimelineHeatmap'
import { CategoryDonut } from './CategoryDonut'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { toast } from 'sonner'

interface DashboardProps {
    initialApps: any[]
    initialKpis: any
    totalApps: number
    initialStatusFlow: any[]
    initialTimeline: any[]
    initialCategories: any[]
}

export function Dashboard({
    initialApps,
    initialKpis,
    totalApps,
    initialStatusFlow,
    initialTimeline,
    initialCategories,
}: DashboardProps) {
    const [apps, setApps] = useState(initialApps)
    const [kpis, setKpis] = useState(initialKpis)
    const [total, setTotal] = useState(totalApps)
    const [page, setPage] = useState(0)
    const [filters, setFilters] = useState({})

    const [statusFlow, setStatusFlow] = useState(initialStatusFlow)
    const [timeline, setTimeline] = useState(initialTimeline)
    const [categories, setCategories] = useState(initialCategories)

    const [selectedApp, setSelectedApp] = useState<any>(null)
    const [historyData, setHistoryData] = useState<any[]>([])
    const [isHistoryOpen, setIsHistoryOpen] = useState(false)

    const refreshData = async () => {
        const { data, total } = await getApplications({ page, size: 10, ...filters })
        setApps(data)
        setTotal(total)

        const newKpis = await getKPIs()
        setKpis(newKpis)

        const [flowRes, timeRes, catRes] = await Promise.all([
            getStatusFlow(),
            getTimelineData(),
            getCategoryData(),
        ])
        if (flowRes.data) setStatusFlow(flowRes.data)
        if (timeRes.data) setTimeline(timeRes.data)
        if (catRes.data) setCategories(catRes.data)
    }

    const handleFilterChange = async (newFilters: any) => {
        setFilters(newFilters)
        setPage(0)
        const { data, total } = await getApplications({ page: 0, size: 10, ...newFilters })
        setApps(data)
        setTotal(total)
    }

    const handlePageChange = async (newPage: number) => {
        setPage(newPage)
        const { data, total } = await getApplications({ page: newPage, size: 10, ...filters })
        setApps(data)
        setTotal(total)
    }

    const handleAddApplication = async (data: any) => {
        const result = await addApplication(data)
        if (result.success) {
            toast.success(`Added ${data.company_name} — ${data.job_title}`)
            refreshData()
        } else {
            toast.error(result.error)
        }
    }

    const handleStatusChange = async (id: number, newStatus: string) => {
        const result = await updateApplicationStatus(id, newStatus)
        if (result.success) {
            toast.success('Status updated')
            refreshData()
        } else {
            toast.error(result.error)
        }
    }

    const handleDeleteApplication = async (id: number) => {
        if (confirm('Are you sure you want to delete this application?')) {
            const result = await deleteApplication(id)
            if (result.success) {
                toast.success('Application deleted')
                refreshData()
            } else {
                toast.error(result.error)
            }
        }
    }

    const handleViewHistory = async (id: number) => {
        const app = apps.find((a: any) => a.id === id)
        if (app) {
            setSelectedApp(app)
            const result = await getApplicationHistory(id)
            if (result.success) {
                setHistoryData(result.data ?? [])
                setIsHistoryOpen(true)
            } else {
                toast.error(result.error)
            }
        }
    }

    const handleAddStatus = async (data: { status: string; notes: string; date: string }) => {
        if (selectedApp) {
            const result = await updateApplicationStatus(selectedApp.id, data.status, data.date, data.notes)
            if (result.success) {
                toast.success('Status updated')
                const historyResult = await getApplicationHistory(selectedApp.id)
                if (historyResult.success) setHistoryData(historyResult.data ?? [])
                refreshData()
            } else {
                toast.error(result.error)
            }
        }
    }

    const handleDeleteHistory = async (historyId: number) => {
        const result = await deleteHistoryItem(historyId)
        if (result.success) {
            toast.success('History entry deleted')
            const historyResult = await getApplicationHistory(selectedApp.id)
            if (historyResult.success) setHistoryData(historyResult.data ?? [])
            refreshData()
        } else {
            toast.error(result.error)
        }
    }

    const handleEditApplication = async (id: number, data: { company_name: string; job_title: string; category: string }) => {
        const result = await updateApplicationDetails(id, data)
        if (result.success) {
            toast.success('Application updated')
            setSelectedApp({ ...selectedApp, ...data })
            refreshData()
        } else {
            toast.error(result.error)
        }
    }

    return (
        <div className="space-y-6">
            {/* Header + KPIs */}
            <div>
                <h1 className="text-2xl font-bold tracking-tight mb-3">Application Tracker</h1>
                <KPIGrid stats={kpis} />
            </div>

            {/* Form (4) + Table (8) side by side */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Add Application Form */}
                <div className="lg:col-span-4">
                    <Card>
                        <CardHeader className="pb-3">
                            <CardTitle className="text-lg">Add Application</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <AddApplicationForm onSubmit={handleAddApplication} />
                        </CardContent>
                    </Card>
                </div>

                {/* Table */}
                <div className="lg:col-span-8">
                    <ApplicationTable
                        data={apps}
                        total={total}
                        page={page}
                        size={10}
                        onPageChange={handlePageChange}
                        onFilterChange={handleFilterChange}
                        onStatusChange={handleStatusChange}
                        onDelete={handleDeleteApplication}
                        onHistory={handleViewHistory}
                    />
                </div>
            </div>

            {/* Charts */}
            <div className="grid gap-6 lg:grid-cols-2">
                <Card>
                    <CardHeader className="pb-3">
                        <CardTitle className="text-lg">Application Timeline</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <TimelineHeatmap data={timeline} />
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="pb-3">
                        <CardTitle className="text-lg">Categories</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <CategoryDonut data={categories} />
                    </CardContent>
                </Card>
            </div>

            <Card>
                <CardHeader className="pb-3">
                    <CardTitle className="text-lg">Status Funnel</CardTitle>
                </CardHeader>
                <CardContent>
                    <StatusFunnel data={statusFlow} />
                </CardContent>
            </Card>

            {/* History Modal */}
            {selectedApp && (
                <StatusHistoryModal
                    isOpen={isHistoryOpen}
                    onClose={() => {
                        setIsHistoryOpen(false)
                        setSelectedApp(null)
                    }}
                    application={selectedApp}
                    history={historyData}
                    onAddStatus={handleAddStatus}
                    onDeleteHistory={handleDeleteHistory}
                    onEditApplication={handleEditApplication}
                />
            )}
        </div>
    )
}
