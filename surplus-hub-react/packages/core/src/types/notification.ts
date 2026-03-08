export interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  isRead: boolean;
  referenceId?: string;
  referenceType?: string;
  createdAt: string;
}

export interface NotificationsResponse {
  data: Notification[];
  unreadCount?: number;
}
