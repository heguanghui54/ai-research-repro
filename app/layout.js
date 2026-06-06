import "./styles.css";

export const metadata = {
  title: "Lumine 论文中文动画解读",
  description: "ByteDance Seed Lumine 论文的中文可视化解读：3D开放世界通用智能体、训练配方、实时推理和跨游戏泛化。",
};

export default function RootLayout({ children }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
