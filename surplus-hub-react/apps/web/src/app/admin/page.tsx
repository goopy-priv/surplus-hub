"use client";

import { useDashboardSummary } from "@repo/core";

interface KpiCardProps {
  label: string;
  value: number | string;
  sub?: string;
  accent?: boolean;
  loading?: boolean;
}

function KpiCard({ label, value, sub, accent, loading }: KpiCardProps) {
  return (
    <div
      className={`rounded-xl border p-5 ${
        accent ? "border-destructive/30 bg-destructive/5" : "border-border bg-card"
      }`}
    >
      <p className="text-xs font-medium text-muted-foreground">{label}</p>
      {loading ? (
        <div className="mt-2 h-8 w-24 animate-pulse rounded bg-muted" />
      ) : (
        <p className={`mt-1 text-2xl font-bold ${accent ? "text-destructive" : "text-foreground"}`}>
          {typeof value === "number" ? value.toLocaleString() : value}
        </p>
      )}
      {sub && <p className="mt-1 text-xs text-muted-foreground">{sub}</p>}
    </div>
  );
}

function ChartPlaceholder({ title }: { title: string }) {
  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <p className="text-sm font-semibold text-foreground">{title}</p>
      <div className="mt-4 flex h-40 items-center justify-center rounded-lg bg-muted">
        <p className="text-xs text-muted-foreground">차트 영역 (추후 구현)</p>
      </div>
    </div>
  );
}

export default function AdminDashboardPage() {
  const { data: summary, isLoading, isError } = useDashboardSummary();

  const pending = summary?.pendingReports ?? 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-foreground">대시보드</h1>
        <p className="mt-1 text-sm text-muted-foreground">서비스 현황을 한눈에 확인하세요.</p>
      </div>

      {isError && (
        <div className="rounded-xl border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive">
          데이터를 불러오는 데 실패했습니다. 잠시 후 다시 시도해주세요.
        </div>
      )}

      {/* KPI 카드 그리드 */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <KpiCard label="총 사용자" value={summary?.totalUsers ?? 0} sub="전체 가입자 수" loading={isLoading} />
        <KpiCard label="활성 사용자" value={summary?.activeUsers ?? 0} sub="최근 30일 기준" loading={isLoading} />
        <KpiCard label="신규 가입 (오늘)" value={summary?.newUsersToday ?? 0} loading={isLoading} />
        <KpiCard
          label="등록 자재"
          value={summary?.totalMaterials ?? 0}
          sub={summary ? `활성: ${summary.activeMaterials.toLocaleString()}개` : undefined}
          loading={isLoading}
        />
        <KpiCard label="총 거래" value={summary?.totalTransactions ?? 0} loading={isLoading} />
        <KpiCard
          label="미처리 신고"
          value={pending}
          accent={pending > 0}
          sub={pending > 0 ? "즉시 검토 필요" : undefined}
          loading={isLoading}
        />
      </div>

      {/* 차트 영역 */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <ChartPlaceholder title="사용자 증가 추이" />
        <ChartPlaceholder title="자재 등록 현황" />
      </div>

      {/* 신고 대기 바로가기 */}
      {!isLoading && pending > 0 && (
        <div className="rounded-xl border border-border bg-card p-5">
          <p className="text-sm font-semibold text-foreground">미처리 신고 대기</p>
          <div className="mt-3 flex items-center justify-between rounded-lg bg-muted px-4 py-3">
            <div>
              <p className="text-sm font-medium text-foreground">
                {pending}건의 신고가 처리를 기다리고 있습니다.
              </p>
              <p className="text-xs text-muted-foreground">즉시 검토가 필요합니다.</p>
            </div>
            <a
              href="/admin/moderation"
              className="rounded-lg bg-primary px-4 py-2 text-xs font-medium text-primary-foreground hover:bg-primary-dark"
            >
              검토하기
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
