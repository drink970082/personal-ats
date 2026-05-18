import { prisma } from '@/lib/db'
import { 
  getApplications, 
  addApplication, 
  updateApplicationStatus, 
  getKPIs 
} from '@/lib/actions'
import { mockDeep, mockReset } from 'jest-mock-extended'
import { PrismaClient } from '@prisma/client'

jest.mock('@/lib/db', () => {
  const { mockDeep } = jest.requireActual('jest-mock-extended')
  return {
    __esModule: true,
    prisma: mockDeep(),
  }
})

const mockPrisma = prisma as unknown as ReturnType<typeof mockDeep<PrismaClient>>

beforeEach(() => {
  mockReset(mockPrisma)
})

describe('Backend Actions', () => {
  describe('getApplications', () => {
    it('should return applications with pagination', async () => {
      const mockApps = [
        { id: 1, company_name: 'Google', job_title: 'SWE', status: 'Applied', category: 'SWE', date_applied: '2023-01-01', notes: '' },
        { id: 2, company_name: 'Meta', job_title: 'MLE', status: 'Applied', category: 'MLE', date_applied: '2023-01-02', notes: '' },
      ]
      
      mockPrisma.applications.findMany.mockResolvedValue(mockApps as any)
      mockPrisma.applications.count.mockResolvedValue(2)

      const result = await getApplications({ page: 0, size: 10 })

      expect(result.data).toHaveLength(2)
      expect(result.total).toBe(2)
      expect(mockPrisma.applications.findMany).toHaveBeenCalledWith(expect.objectContaining({
        skip: 0,
        take: 10,
        orderBy: { date_applied: 'desc' }
      }))
    })

    it('should filter by status', async () => {
      mockPrisma.applications.findMany.mockResolvedValue([])
      mockPrisma.applications.count.mockResolvedValue(0)

      await getApplications({ page: 0, size: 10, status: 'Applied' })

      expect(mockPrisma.applications.findMany).toHaveBeenCalledWith(expect.objectContaining({
        where: expect.objectContaining({
          AND: expect.arrayContaining([
            expect.objectContaining({ status: 'Applied' })
          ])
        })
      }))
    })

    it('should filter by search term', async () => {
      mockPrisma.applications.findMany.mockResolvedValue([])
      mockPrisma.applications.count.mockResolvedValue(0)

      await getApplications({ page: 0, size: 10, search: 'Google' })

      expect(mockPrisma.applications.findMany).toHaveBeenCalledWith(expect.objectContaining({
        where: expect.objectContaining({
          AND: expect.arrayContaining([
            expect.objectContaining({
              OR: expect.arrayContaining([
                expect.objectContaining({ company_name: { contains: 'Google' } })
              ])
            })
          ])
        })
      }))
    })
  })

  describe('addApplication', () => {
    it('should add a valid application', async () => {
      const newApp = {
        company_name: 'Amazon',
        job_title: 'SDE',
        date_applied: '2023-01-03',
        category: 'SWE',
        status: 'Applied',
        application_url: '',
        notes: ''
      }

      mockPrisma.applications.findFirst.mockResolvedValue(null)
      mockPrisma.applications.create.mockResolvedValue({ id: 3, ...newApp } as any)

      const result = await addApplication(newApp)

      expect(result.success).toBe(true)
      expect(mockPrisma.applications.create).toHaveBeenCalled()
    })

    it('should fail if duplicate exists', async () => {
      const newApp = {
        company_name: 'Amazon',
        job_title: 'SDE',
        date_applied: '2023-01-03',
        category: 'SWE',
        status: 'Applied'
      }

      mockPrisma.applications.findFirst.mockResolvedValue({ id: 1 } as any)

      const result = await addApplication(newApp)

      expect(result.success).toBe(false)
      expect(result.error).toContain('already exists')
      expect(mockPrisma.applications.create).not.toHaveBeenCalled()
    })
  })

  describe('updateApplicationStatus', () => {
    it('should update status and add history', async () => {
      const appId = 1
      const newStatus = 'Interviewing: 1st round'
      
      mockPrisma.applications.findUnique.mockResolvedValue({ id: appId, status: 'Applied' } as any)
      mockPrisma.$transaction.mockImplementation(async (callback) => await callback(mockPrisma))

      const result = await updateApplicationStatus(appId, newStatus)

      expect(result.success).toBe(true)
      expect(mockPrisma.applications.update).toHaveBeenCalledWith(expect.objectContaining({
        where: { id: appId },
        data: expect.objectContaining({ status: newStatus })
      }))
      expect(mockPrisma.status_history.create).toHaveBeenCalledWith(expect.objectContaining({
        data: expect.objectContaining({
          application_id: appId,
          status: newStatus
        })
      }))
    })
  })

  describe('getKPIs', () => {
    it('should calculate KPIs correctly', async () => {
      const mockApps = [
        { status: 'Applied' },
        { status: 'Applied' },
        { status: 'Rejected' },
        { status: 'Offer' },
        { status: 'Interviewing: 1st round' },
      ]

      mockPrisma.applications.findMany.mockResolvedValue(mockApps as any)

      const kpis = await getKPIs()

      expect(kpis.applied).toBe(5) // total count
      expect(kpis.rejected).toBe(1)
      expect(kpis.offer).toBe(1)
      expect(kpis.interviewing).toBe(1)
      expect(kpis.active).toBe(3) // Total - Rejected - Offer = 5 - 1 - 1
    })
  })
})
