export type NavItem = {
  href: string;
  label: string;
};

export const NAV_ITEMS: NavItem[] = [
  { href: "/", label: "홈" },
  { href: "/search", label: "검색" },
  { href: "/chat", label: "채팅" },
  { href: "/community", label: "커뮤니티" },
  { href: "/profile", label: "프로필" },
];

export const DESKTOP_NAV_ITEMS: NavItem[] = [
  { href: "/", label: "홈" },
  { href: "/community", label: "커뮤니티" },
  { href: "/chat", label: "채팅" },
  { href: "/notifications", label: "알림" },
  { href: "/profile", label: "프로필" },
];
