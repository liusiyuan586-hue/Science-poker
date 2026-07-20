import type { Metadata } from "next";
import "./globals.css";
import "katex/dist/katex.min.css";
import "./enhancements.css";

export const metadata: Metadata = {
  title: "自然科学文明扑克",
  description: "用 216 张知识卡牌探索数学、物理、自然科学与计算机科学。",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="zh-CN"><body>{children}</body></html>;
}
