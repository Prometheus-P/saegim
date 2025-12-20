import Head from 'next/head';
import Link from 'next/link';

export default function Home() {
  return (
    <>
      <Head>
        <title>새김 (Saegim) · 배송 증빙</title>
        <meta name="description" content="QR 기반 배송/행사 증빙 링크 생성 및 사진 인증" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <main className="page">
        <div className="container">
          <div className="card">
            <div className="brand" style={{ marginBottom: 12 }}>
              <div className="name">새김</div>
              <div className="tag">QR 기반 배송·행사 증빙</div>
            </div>

            <div className="grid3" style={{ marginTop: 14 }}>
              <div className="card flat">
                <div style={{ fontWeight: 800, marginBottom: 6 }}>현장</div>
                <div className="muted">QR 스캔 → 사진 1장 → 업로드</div>
              </div>
              <div className="card flat">
                <div style={{ fontWeight: 800, marginBottom: 6 }}>구매자</div>
                <div className="muted">로그인 없이 링크로 확인</div>
              </div>
              <div className="card flat">
                <div style={{ fontWeight: 800, marginBottom: 6 }}>업체</div>
                <div className="muted">클레임 방어 + CS 비용 절감</div>
              </div>
            </div>

            <div className="row" style={{ marginTop: 16 }}>
              <Link className="btn" href="/app">업체용 백오피스</Link>
              <a className="btn secondary" href="/docs" style={{ pointerEvents: 'none', opacity: 0.6 }}>
                (v1) 문서
              </a>
            </div>

            <div className="muted" style={{ marginTop: 14 }}>
              운영자: <code className="code">/app</code> → Orders → 주문 생성 → 토큰 발급 → QR 출력
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
