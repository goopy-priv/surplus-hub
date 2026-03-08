"use client";

import { useRouter } from "next/navigation";
import { useEvents } from "@repo/core";

const formatDate = (value: string): string => {
  const d = new Date(value);
  if (!Number.isFinite(d.getTime())) return "";
  return d.toLocaleDateString("ko-KR", { year: "numeric", month: "short", day: "numeric" });
};

const isEventOngoing = (startDate: string, endDate: string): boolean => {
  const now = Date.now();
  return new Date(startDate).getTime() <= now && now <= new Date(endDate).getTime();
};

export default function EventsPage() {
  const router = useRouter();
  const { data, isLoading, error } = useEvents({ page: 1, limit: 20 });
  const events = data?.data ?? [];

  return (
    <div className="min-h-screen bg-background">
      <div className="border-b border-border bg-card px-4 py-6">
        <h1 className="mb-2 text-xl font-bold text-foreground md:hidden">이벤트 & 프로모션</h1>
        <p className="text-sm text-muted-foreground">
          진행 중인 이벤트와 혜택을 확인하세요.
        </p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-primary" />
        </div>
      ) : null}

      {error ? (
        <div className="p-8 text-center text-sm text-red-500">이벤트를 불러오지 못했습니다.</div>
      ) : null}

      {!isLoading && !error ? (
        <div className="p-4 space-y-3">
          {events.map((event) => {
            const ongoing = isEventOngoing(event.startDate, event.endDate);

            return (
              <div
                key={event.id}
                onClick={() => router.push(`/events/${event.id}`)}
                className="cursor-pointer overflow-hidden rounded-xl border border-border bg-card shadow-sm transition-shadow hover:shadow-md active:bg-muted/50"
              >
                {event.imageUrl ? (
                  <div className="h-40 w-full overflow-hidden bg-muted">
                    <img
                      src={event.imageUrl}
                      alt={event.title}
                      className="h-full w-full object-cover"
                    />
                  </div>
                ) : (
                  <div className="flex h-40 w-full items-center justify-center bg-gradient-to-br from-primary/10 to-primary/5">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={1.5}
                      stroke="currentColor"
                      className="h-12 w-12 text-primary/40"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z"
                      />
                    </svg>
                  </div>
                )}

                <div className="p-4">
                  <div className="mb-2 flex items-center gap-2">
                    <span
                      className={`inline-block rounded-full px-2 py-0.5 text-[10px] font-semibold ${
                        ongoing
                          ? "bg-green-100 text-green-700"
                          : event.isActive
                          ? "bg-blue-100 text-blue-700"
                          : "bg-gray-100 text-gray-500"
                      }`}
                    >
                      {ongoing ? "진행중" : event.isActive ? "예정" : "종료"}
                    </span>
                  </div>

                  <h3 className="mb-1 text-sm font-bold text-foreground">{event.title}</h3>
                  <p className="mb-3 line-clamp-2 text-xs text-muted-foreground">{event.description}</p>

                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={1.5}
                      stroke="currentColor"
                      className="h-3.5 w-3.5"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0v-7.5A2.25 2.25 0 0 1 5.25 9h13.5A2.25 2.25 0 0 1 21 11.25v7.5"
                      />
                    </svg>
                    <span>{formatDate(event.startDate)} ~ {formatDate(event.endDate)}</span>
                  </div>
                </div>
              </div>
            );
          })}

          {events.length === 0 ? (
            <div className="rounded-xl border border-dashed border-border bg-card p-8 text-center text-sm text-muted-foreground">
              진행 중인 이벤트가 없습니다.
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
