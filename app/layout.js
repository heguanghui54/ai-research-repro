import "./styles.css";

export const metadata = {
  title: "健身气功短视频人工编码平台",
  description: "用于健身气功短视频传播延异研究的多人协同人工编码平台",
};

export default function RootLayout({ children }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
