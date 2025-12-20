import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="page">
      <div className="container sm">
        <div className="card">
          <div style={{ fontSize: 18, fontWeight: 800, marginBottom: 6 }}>페이지를 찾을 수 없습니다</div>
          <div className="muted" style={{ marginBottom: 14 }}>링크가 틀렸거나, 만료됐을 수 있습니다.</div>
          <Link className="btn secondary" href="/">홈으로</Link>
        </div>
      </div>
    </div>
  );
}
