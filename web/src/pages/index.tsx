import Head from 'next/head';

export default function Home() {
  return (
    <>
      <Head>
        <title>ProofLink - 배송 증빙 시스템</title>
        <meta name="description" content="QR 기반 배송 증빙 및 알림 서비스" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <main style={styles.main}>
        <div style={styles.container}>
          <h1 style={styles.title}>ProofLink</h1>
          <p style={styles.subtitle}>QR 기반 배송 증빙 시스템</p>

          <div style={styles.features}>
            <div style={styles.feature}>
              <span style={styles.emoji}>📱</span>
              <h3>QR 스캔</h3>
              <p>QR 코드를 스캔하면 바로 증빙 업로드</p>
            </div>
            <div style={styles.feature}>
              <span style={styles.emoji}>📸</span>
              <h3>원탭 촬영</h3>
              <p>카메라로 촬영 즉시 업로드 완료</p>
            </div>
            <div style={styles.feature}>
              <span style={styles.emoji}>🔔</span>
              <h3>실시간 알림</h3>
              <p>발주자와 수령인에게 동시 알림</p>
            </div>
          </div>

          <div style={styles.info}>
            <p>화원사 대시보드는 준비 중입니다.</p>
            <p style={styles.hint}>
              테스트: <code>/proof/test123token</code>
            </p>
          </div>
        </div>
      </main>

      <style jsx global>{`
        * {
          box-sizing: border-box;
          margin: 0;
          padding: 0;
        }
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          min-height: 100vh;
        }
        code {
          background: rgba(0,0,0,0.1);
          padding: 2px 6px;
          border-radius: 4px;
          font-size: 0.9em;
        }
      `}</style>
    </>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  main: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '20px',
  },
  container: {
    background: 'white',
    borderRadius: '16px',
    padding: '40px',
    maxWidth: '600px',
    width: '100%',
    textAlign: 'center',
    boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
  },
  title: {
    fontSize: '2.5rem',
    color: '#333',
    marginBottom: '8px',
  },
  subtitle: {
    fontSize: '1.1rem',
    color: '#666',
    marginBottom: '32px',
  },
  features: {
    display: 'flex',
    gap: '20px',
    marginBottom: '32px',
    flexWrap: 'wrap' as const,
    justifyContent: 'center',
  },
  feature: {
    flex: '1 1 150px',
    padding: '16px',
    background: '#f8f9fa',
    borderRadius: '12px',
    minWidth: '140px',
  },
  emoji: {
    fontSize: '2rem',
    display: 'block',
    marginBottom: '8px',
  },
  info: {
    color: '#888',
    fontSize: '0.9rem',
  },
  hint: {
    marginTop: '8px',
  },
};
