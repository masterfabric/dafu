import type { Metadata, Viewport } from "next";
import { Fira_Code } from "next/font/google";
import "./globals.css";

const firaCode = Fira_Code({ 
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-fira-code"
});

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#1e40af',
}

export const metadata: Metadata = {
  metadataBase: new URL('https://dafu.masterfabric.co'),
  title: "DAFU - Enterprise Fraud Detection & Analytics Platform",
  description: "Comprehensive fraud detection and e-commerce analytics platform designed for enterprise deployment. Advanced machine learning-based fraud detection with anomaly detection and sequence analysis.",
  keywords: [
    "fraud detection",
    "machine learning",
    "enterprise analytics",
    "e-commerce security",
    "anomaly detection",
    "LSTM",
    "GRU",
    "isolation forest",
    "real-time fraud detection",
    "FastAPI",
    "Kubernetes",
    "microservices"
  ],
  authors: [{ name: "MasterFabric" }],
  creator: "MasterFabric",
  publisher: "MasterFabric",
  robots: "index, follow",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://dafu.masterfabric.co",
    siteName: "DAFU - Data Analytics Functional Utilities",
    title: "DAFU - Enterprise Fraud Detection & Analytics Platform",
    description: "Advanced machine learning-based fraud detection capabilities with anomaly detection and sequence analysis for enterprise deployment.",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "DAFU Platform Overview",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "DAFU - Enterprise Fraud Detection & Analytics Platform",
    description: "Advanced ML-based fraud detection with sub-50ms response time and 99.9% uptime SLA",
    images: ["/og-image.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const today = new Date().toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <html lang="en">
      <head>
        <link rel="canonical" href="https://dafu.masterfabric.co" />
        <meta name="application-name" content="DAFU Platform" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="DAFU" />
        <meta name="format-detection" content="telephone=no" />
        <meta name="mobile-web-app-capable" content="yes" />
        
        {/* Structured Data for SEO */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "SoftwareApplication",
              "name": "DAFU - Data Analytics Functional Utilities",
              "applicationCategory": "SecurityApplication",
              "operatingSystem": "Cross-platform",
              "description": "Enterprise fraud detection and e-commerce analytics platform with advanced machine learning capabilities",
              "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
              "author": {"@type": "Organization", "name": "MasterFabric", "url": "https://dafu.masterfabric.co"}
            })
          }}
        />
      </head>
      <body className={firaCode.className}>
        {children}
        <div className="hr" />
        <footer style={{ textAlign: 'center', paddingBottom: '2rem' }}>
          <p className="muted">© 2025 MasterFabric · AGPL-3.0</p>
          <p style={{ marginTop: '0.5rem' }}>
            <span className="muted">Source: </span>
            <a href="https://github.com/masterfabric/dafu/" target="_blank" rel="noopener noreferrer">github.com/masterfabric/dafu</a>
          </p>
          <p>
            <span className="muted">Contact: </span>
            <a href="mailto:dafu@masterfabric.co">dafu@masterfabric.co</a>
          </p>
          <p className="muted" style={{ marginTop: '0.5rem' }}>Last updated: {today}</p>
        </footer>
      </body>
    </html>
  );
}
