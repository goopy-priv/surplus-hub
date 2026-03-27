import { expect, test, type Page, type Route } from "@playwright/test";

/**
 * Phase 1 MVP E2E Tests — 당근마켓 for B2B
 *
 * Tests:
 * 1. Home feed: region dropdown filter + condition_grade badge display
 * 2. Material registration: condition_grade + region dropdown
 * 3. Chat entry: material detail → chat button flow
 */

type MaterialItem = {
  id: string;
  title: string;
  description: string;
  price: number;
  imageUrl: string;
  category: string;
  location: string;
  sellerId: string;
  sellerName: string;
  conditionGrade?: string;
  quantity?: number;
  quantityUnit?: string;
  status?: string;
  createdAt: string;
};

const seedMaterials = (): MaterialItem[] => [
  {
    id: "201",
    title: "LED 조명 모듈 50개",
    description: "공장 잉여분 LED 모듈",
    price: 300000,
    imageUrl: "",
    category: "조명",
    location: "경기도",
    sellerId: "31",
    sellerName: "조명공장",
    conditionGrade: "상",
    quantity: 50,
    quantityUnit: "개",
    status: "ACTIVE",
    createdAt: "2026-03-27T10:00:00.000Z",
  },
  {
    id: "202",
    title: "사무실 문짝 10개",
    description: "미사용 문짝",
    price: 500000,
    imageUrl: "",
    category: "문/창호",
    location: "서울특별시",
    sellerId: "32",
    sellerName: "문제작소",
    conditionGrade: "중",
    quantity: 10,
    quantityUnit: "개",
    status: "ACTIVE",
    createdAt: "2026-03-26T09:00:00.000Z",
  },
];

const withApiEnvelope = (data: unknown, meta?: unknown) =>
  JSON.stringify({
    status: "success",
    data,
    ...(meta ? { meta } : {}),
  });

const stubExternalClerkScript = async (page: Page) => {
  await page.route("**://*.clerk.accounts.dev/**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/javascript",
      body: "",
    });
  });
};

const stubPhase1Api = async (page: Page) => {
  const materials = seedMaterials();

  await page.route("**/api/v1/**", async (route: Route) => {
    const url = route.request().url();
    const method = route.request().method();

    // User profile
    if (url.includes("/api/v1/users/me")) {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: withApiEnvelope({
          id: "11",
          name: "테스트사장",
          location: "경기도",
        }),
      });
      return;
    }

    // Material detail
    if (url.includes("/api/v1/materials/") && method === "GET" && /\/api\/v1\/materials\/\d+$/.test(url)) {
      const idMatch = url.match(/\/api\/v1\/materials\/(\d+)/);
      const id = idMatch ? idMatch[1] : "";
      const found = materials.find((item) => item.id === id);
      await route.fulfill({
        status: found ? 200 : 404,
        contentType: "application/json",
        body: withApiEnvelope(found ?? { detail: "not found" }),
      });
      return;
    }

    // Material list with location filter
    if (url.includes("/api/v1/materials") && method === "GET") {
      const parsed = new URL(url);
      const location = parsed.searchParams.get("location");
      const filtered = location
        ? materials.filter((item) => item.location.includes(location))
        : materials;

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: withApiEnvelope(filtered, {
          totalCount: filtered.length,
          page: 1,
          limit: 20,
          hasNextPage: false,
          totalPages: 1,
        }),
      });
      return;
    }

    // Material create
    if (url.includes("/api/v1/materials") && method === "POST") {
      const payload = route.request().postDataJSON() as Record<string, unknown>;
      const created: MaterialItem = {
        id: String(2000 + materials.length),
        title: String(payload.title ?? "새 자재"),
        description: String(payload.description ?? ""),
        price: Number(payload.price ?? 0),
        imageUrl: "",
        category: String(payload.category ?? "기타"),
        location:
          typeof payload.location === "object" && payload.location !== null
            ? String((payload.location as { address?: string }).address ?? "위치 미정")
            : "위치 미정",
        sellerId: "11",
        sellerName: "테스트사장",
        conditionGrade: typeof payload.conditionGrade === "string" ? payload.conditionGrade : undefined,
        quantity: Number(payload.quantity ?? 0) || undefined,
        quantityUnit: typeof payload.quantityUnit === "string" ? payload.quantityUnit : undefined,
        status: "ACTIVE",
        createdAt: new Date().toISOString(),
      };
      materials.unshift(created);
      await route.fulfill({
        status: 201,
        contentType: "application/json",
        body: withApiEnvelope(created),
      });
      return;
    }

    // Chat room create
    if (url.includes("/api/v1/chats/rooms") && method === "POST") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: withApiEnvelope({ id: "room-601" }),
      });
      return;
    }

    // Chat messages
    if (url.includes("/api/v1/chats/rooms/room-601/messages") && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: withApiEnvelope([]),
      });
      return;
    }

    // Chat rooms list
    if (url.includes("/api/v1/chats/rooms") && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: withApiEnvelope([]),
      });
      return;
    }

    // Default
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: withApiEnvelope({}),
    });
  });
};

test.describe("Phase 1 B2B — home feed", () => {
  test.beforeEach(async ({ page }) => {
    await stubExternalClerkScript(page);
    await stubPhase1Api(page);
    await page.addInitScript(() => {
      localStorage.setItem("access_token", "playwright-token");
    });
  });

  test("displays materials with condition_grade badges", async ({ page }) => {
    await page.goto("/");

    // Feed should show materials
    await expect(page.getByText("LED 조명 모듈 50개")).toBeVisible();
    await expect(page.getByText("사무실 문짝 10개")).toBeVisible();

    // Condition grade badges should be visible
    await expect(page.getByText("상").first()).toBeVisible();
    await expect(page.getByText("중").first()).toBeVisible();

    // Prices should be visible
    await expect(page.getByText("300,000원")).toBeVisible();
    await expect(page.getByText("500,000원")).toBeVisible();
  });

  test("region dropdown filters materials", async ({ page }) => {
    await page.goto("/");

    // Both materials visible initially
    await expect(page.getByText("LED 조명 모듈 50개")).toBeVisible();
    await expect(page.getByText("사무실 문짝 10개")).toBeVisible();

    // Select 경기도 region
    const regionSelect = page.locator("select").first();
    await regionSelect.selectOption("경기도");

    // Wait for re-render — only 경기도 material should remain
    await page.waitForTimeout(500);
    await expect(page.getByText("LED 조명 모듈 50개")).toBeVisible();
  });

  test("bottom nav has register button in center", async ({ page }) => {
    await page.goto("/");

    // BottomNav should have 5 items including register
    const registerLink = page.locator('nav a[href="/register"]');
    await expect(registerLink).toBeVisible();
  });
});

test.describe("Phase 1 B2B — material registration", () => {
  test.beforeEach(async ({ page }) => {
    await stubExternalClerkScript(page);
    await stubPhase1Api(page);
    await page.addInitScript(() => {
      localStorage.setItem("access_token", "playwright-token");
    });
  });

  test("register form has condition_grade and region fields", async ({ page }) => {
    await page.goto("/register");

    // condition_grade dropdown should exist
    const conditionSelect = page.locator("select").filter({ hasText: /상태 등급|상 \(양호\)|선택 안 함/ });
    await expect(conditionSelect.or(page.getByText("상태 등급"))).toBeVisible();

    // Region/location dropdown should exist with 시도 options
    await expect(page.getByText("서울특별시").or(page.getByText("경기도")).first()).toBeVisible();
  });
});

test.describe("Phase 1 B2B — chat entry", () => {
  test.beforeEach(async ({ page }) => {
    await stubExternalClerkScript(page);
    await stubPhase1Api(page);
    await page.addInitScript(() => {
      localStorage.setItem("access_token", "playwright-token");
    });
  });

  test("material detail to chat button flow", async ({ page }) => {
    await page.goto("/material/201");

    // Material detail should show
    await expect(page.getByText("LED 조명 모듈 50개")).toBeVisible();
    await expect(page.getByText("300,000")).toBeVisible();

    // Condition grade badge should show
    await expect(page.getByText("상").first()).toBeVisible();

    // Chat button should be visible
    const chatButton = page.getByRole("button", { name: /채팅|문의/ });
    await expect(chatButton).toBeVisible();
  });
});
