import "./globals.css";


export const metadata = {
  title: "Contract Assesment",
  description: "Created by X-trios",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/logobw.png" />
      </head>
      <body>{children}</body>
    </html>
  );
}
