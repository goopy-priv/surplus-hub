"use client";

import { useUser } from "@clerk/nextjs";
import { useAuditLogs } from "@repo/core";

export default function AdminSettingsPage() {
  const { user } = useUser();
  const { data: auditData, isLoading: auditLoading } = useAuditLogs({ limit: 10 });

  const adminName = user?.fullName ?? user?.username ?? "관리자";
  const adminEmail = user?.emailAddresses[0]?.emailAddress ?? "";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-foreground">설정</h1>
        <p className="mt-1 text-sm text-muted-foreground">관리자 정보 및 시스템 설정을 확인합니다.</p>
      </div>

      {/* 관리자 정보 */}
      <section className="rounded-xl border border-border bg-card p-5">
        <h2 className="text-sm font-semibold text-foreground">내 관리자 정보</h2>
        <div className="mt-4 flex items-center gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-accent text-accent-foreground text-xl font-bold">
            {adminName[0] ?? "A"}
          </div>
          <div>
            <p className="font-semibold text-foreground">{adminName}</p>
            <p className="text-sm text-muted-foreground">{adminEmail || "이메일 없음"}</p>
          </div>
        </div>
        <div className="mt-4 grid grid-cols-2 gap-3 text-sm sm:grid-cols-3">
          <div className="rounded-lg bg-muted p-3">
            <p className="text-xs text-muted-foreground">역할</p>
            <p className="mt-0.5 font-medium text-foreground">슈퍼관리자</p>
          </div>
          <div className="rounded-lg bg-muted p-3">
            <p className="text-xs text-muted-foreground">가입일</p>
            <p className="mt-0.5 font-medium text-foreground">
              {user?.createdAt ? new Date(user.createdAt).toLocaleDateString("ko-KR") : "-"}
            </p>
          </div>
          <div className="rounded-lg bg-muted p-3">
            <p className="text-xs text-muted-foreground">마지막 로그인</p>
            <p className="mt-0.5 font-medium text-foreground">
              {user?.lastSignInAt ? new Date(user.lastSignInAt).toLocaleDateString("ko-KR") : "-"}
            </p>
          </div>
        </div>
      </section>

      {/* 시스템 설정 */}
      <section className="rounded-xl border border-border bg-card p-5">
        <h2 className="text-sm font-semibold text-foreground">시스템 설정</h2>
        <p className="mt-1 text-xs text-muted-foreground">Phase 1.2에서 구현 예정입니다.</p>
        <div className="mt-4 space-y-3">
          {[
            { label: "이메일 알림", desc: "신고 접수 시 이메일 수신" },
            { label: "자동 필터링", desc: "금칙어 자동 차단 활성화" },
            { label: "유지보수 모드", desc: "서비스 임시 점검 모드" },
          ].map((item) => (
            <div key={item.label} className="flex items-center justify-between rounded-lg border border-border p-3">
              <div>
                <p className="text-sm font-medium text-foreground">{item.label}</p>
                <p className="text-xs text-muted-foreground">{item.desc}</p>
              </div>
              <div className="h-5 w-9 rounded-full bg-muted opacity-50 cursor-not-allowed" />
            </div>
          ))}
        </div>
      </section>

      {/* 감사 로그 */}
      <section className="rounded-xl border border-border bg-card p-5">
        <h2 className="text-sm font-semibold text-foreground">최근 감사 로그</h2>
        <p className="mt-1 text-xs text-muted-foreground">관리자 활동 내역입니다.</p>
        <div className="mt-4 space-y-2">
          {auditLoading ? (
            Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="h-10 animate-pulse rounded-lg bg-muted" />
            ))
          ) : (auditData?.items ?? []).length === 0 ? (
            <p className="py-6 text-center text-xs text-muted-foreground">감사 로그가 없습니다.</p>
          ) : (
            (auditData?.items ?? []).map((log) => (
              <div key={log.id} className="flex items-start justify-between gap-3 rounded-lg bg-muted/50 px-3 py-2.5">
                <div className="min-w-0">
                  <p className="text-xs font-medium text-foreground">{log.action}</p>
                  {log.targetType && log.targetId && (
                    <p className="mt-0.5 text-xs text-muted-foreground truncate">
                      {log.targetType} #{log.targetId}
                      {log.details ? ` · ${log.details}` : ""}
                    </p>
                  )}
                </div>
                <div className="flex-shrink-0 text-right">
                  <p className="text-xs text-muted-foreground">관리자 #{log.adminId}</p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(log.createdAt).toLocaleDateString("ko-KR")}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>
      </section>
    </div>
  );
}
