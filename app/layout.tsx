import type { Metadata } from "next";
import { headers } from "next/headers";
import "./globals.css";
import "katex/dist/katex.min.css";
import "./enhancements.css";

const title = "科学文明扑克 · Science Poker";
const description = "用 216 张知识卡牌探索数学、物理、自然科学与计算机科学。翻开一张牌，进入一个改变世界的思想。";

export async function generateMetadata(): Promise<Metadata> {
  const requestHeaders = await headers();
  const host = requestHeaders.get("x-forwarded-host") ?? requestHeaders.get("host") ?? "localhost:3000";
  const protocol = requestHeaders.get("x-forwarded-proto") ?? (host.startsWith("localhost") ? "http" : "https");
  const image = `${protocol}://${host}/og.png`;

  return {
    title,
    description,
    openGraph: { title, description, type: "website", images: [{ url: image, width: 1200, height: 630, alt: title }] },
    twitter: { card: "summary_large_image", title, description, images: [image] },
  };
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="zh-CN"><body>{children}</body></html>;
}
