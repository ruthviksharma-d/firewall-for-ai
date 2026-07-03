/**
 * Typed client functions for the Milestone 4 admin APIs. Every dashboard
 * page calls through here via TanStack Query - no component talks to
 * axios directly, and no component hardcodes a response shape.
 */
import { api } from "./api"
import type {
  AnalyticsSummary,
  CompanyKeyword,
  DashboardSummary,
  EmployeeListResponse,
  OrgSettings,
  Policy,
  PolicyInput,
  PromptLogDetail,
  PromptLogListResponse,
} from "@/types/admin"

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const { data } = await api.get<DashboardSummary>("/api/dashboard/summary")
  return data
}

export async function getAnalyticsSummary(): Promise<AnalyticsSummary> {
  const { data } = await api.get<AnalyticsSummary>("/api/analytics/summary")
  return data
}

export interface PromptLogFilters {
  page?: number
  page_size?: number
  search?: string
  action?: string
  risk?: string
  website?: string
  sort_by?: "created_at" | "score"
  sort_dir?: "asc" | "desc"
}

export async function getPromptLogs(filters: PromptLogFilters): Promise<PromptLogListResponse> {
  const { data } = await api.get<PromptLogListResponse>("/api/prompt-logs", { params: filters })
  return data
}

export async function getPromptLogDetail(id: string): Promise<PromptLogDetail> {
  const { data } = await api.get<PromptLogDetail>(`/api/prompt-logs/${id}`)
  return data
}

export async function getPolicies(): Promise<Policy[]> {
  const { data } = await api.get<Policy[]>("/api/policies")
  return data
}

export async function createPolicy(payload: PolicyInput): Promise<Policy> {
  const { data } = await api.post<Policy>("/api/policies", payload)
  return data
}

export async function updatePolicy(id: string, payload: Partial<PolicyInput>): Promise<Policy> {
  const { data } = await api.patch<Policy>(`/api/policies/${id}`, payload)
  return data
}

export async function deletePolicy(id: string): Promise<void> {
  await api.delete(`/api/policies/${id}`)
}

export interface EmployeeFilters {
  page?: number
  page_size?: number
  search?: string
  department?: string
  role?: string
}

export async function getEmployees(filters: EmployeeFilters): Promise<EmployeeListResponse> {
  const { data } = await api.get<EmployeeListResponse>("/api/employees", { params: filters })
  return data
}

export async function getSettings(): Promise<OrgSettings> {
  const { data } = await api.get<OrgSettings>("/api/settings")
  return data
}

export async function updateSettings(payload: Partial<OrgSettings>): Promise<OrgSettings> {
  const { data } = await api.put<OrgSettings>("/api/settings", payload)
  return data
}

export async function getKeywords(): Promise<CompanyKeyword[]> {
  const { data } = await api.get<CompanyKeyword[]>("/api/settings/keywords")
  return data
}

export async function createKeyword(keyword: string): Promise<CompanyKeyword> {
  const { data } = await api.post<CompanyKeyword>("/api/settings/keywords", { keyword })
  return data
}

export async function updateKeyword(id: string, enabled: boolean): Promise<CompanyKeyword> {
  const { data } = await api.patch<CompanyKeyword>(`/api/settings/keywords/${id}`, { enabled })
  return data
}

export async function deleteKeyword(id: string): Promise<void> {
  await api.delete(`/api/settings/keywords/${id}`)
}
