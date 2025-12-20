import { useRouter } from 'next/router';
import { useEffect, useMemo, useState } from 'react';
import { getProofByToken, ProofData } from '../../services/api';


const copy = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
};

export default function PublicProofPage() {
  const router = useRouter();
  const { token } = router.query;
  const t = typeof token === 'string' ? token : '';

  const [proof, setProof] = useState<ProofData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    if (!t) return;
    (async () => {
      setLoading(true);
      setError(null);
      const data = await getProofByToken(t);
      if (!data) {
        setError('유효하지 않은 링크입니다.');
        return;
      }
      setProof(data);
    })()
      .catch((err: any) => {
        if (err?.message === 'RATE_LIMITED') setError('요청이 너무 많습니다. 잠시 후 다시 시도해주세요.');
        else setError('증빙 정보를 불러오는데 실패했습니다.');
      })
      .finally(() => setLoading(false));
  }, [t]);

  const proofUrl = useMemo(() => {
    if (!proof?.proof_url) return '';
    if (proof.proof_url.startsWith('http')) return proof.proof_url;
    const api = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';
    const origin = api.replace(/\/api\/v1\/?$/, '');

  const shareUrl = useMemo(() => {
    if (typeof window === 'undefined') return '';
    return window.location.href;
  }, [t]);

  const canShare = typeof navigator !== 'undefined' && !!(navigator as any).share;

  const share = async () => {
    try {
      if (!canShare) return;
      const title = '배송 완료 증빙';
      const lines = [
        proof?.organization_name ? proof.organization_name : '',
        proof?.context ? String(proof.context) : '',
        proof?.order_number ? `주문번호: ${proof.order_number}` : '',
      ].filter(Boolean);
      const text = lines.join('\n');
      await (navigator as any).share({ title, text, url: shareUrl });
      setToast('공유됨');
    } catch (e) {
      // user cancel or share failed: ignore
    } finally {
      window.setTimeout(() => setToast(null), 1400);
    }
  };
    return `${origin}${proof.proof_url}`;
  }, [proof]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="page">
      <div className="container sm">
        <div className="card flat" style={{ marginBottom: 14, textAlign: 'center' }}>
          {proof?.organization_logo && (
            <img
              src={proof.organization_logo}
              alt={proof.organization_name}
              style={{ maxWidth: 140, maxHeight: 48, objectFit: 'contain', marginBottom: 10 }}
            />
          )}
          <div style={{ fontSize: 18, fontWeight: 800 }}>배송 완료</div>
          <div className="muted" style={{ marginTop: 6 }}>
            {proof?.organization_name || '새김'}
          </div>
          {proof && !proof.hide_saegim && (
            <div className="muted" style={{ marginTop: 4, fontSize: 12 }}>Powered by 새김</div>
          )}
        </div>

        {loading && <div className="muted">로딩 중…</div>}

        {!loading && error && (
          <div className="danger">
            <div style={{ fontWeight: 700, marginBottom: 6 }}>오류</div>
            <div>{error}</div>
          </div>
        )}

        {!loading && proof && (
          <div className="stack">
            <div className="card flat">
              <div className="row" style={{ justifyContent: 'space-between' }}>
                <div>
                  <div className="label">주문번호</div>
                  <div style={{ fontWeight: 800 }}>{proof.order_number}</div>
                  {proof.context && <div className="muted" style={{ marginTop: 4 }}>{proof.context}</div>}
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div className="label">업로드 시각</div>
                  <div style={{ fontWeight: 700 }}>{formatDate(proof.uploaded_at)}</div>
                </div>
              </div>
            </div>

            <div className="card">
              {proofUrl ? (
                <img
                  src={proofUrl}
                  alt="배송 증빙 사진"
                  style={{ width: '100%', borderRadius: 16, border: '1px solid var(--line)' }}
                />
              ) : (
                <div className="muted">증빙 이미지가 없습니다.</div>
              )}
              {proofUrl && (
                <div style={{ marginTop: 10 }}>
                  <a className="btn secondary" href={proofUrl} target="_blank" rel="noreferrer">
                    원본 열기
                  </a>
                </div>
              )}
              <div className="row" style={{ marginTop: 10, justifyContent: 'center' }}>
                <button
                  className="btn"
                  onClick={async () => {
                    const ok = await copy(shareUrl || '');
                    setToast(ok ? '링크 복사됨' : '복사 실패');
                    window.setTimeout(() => setToast(null), 1400);
                  }}
                  disabled={!shareUrl}
                >
                  링크 복사
                </button>
                {canShare && (
                  <button className="btn secondary" onClick={share} disabled={!shareUrl}>
                    공유
                  </button>
                )}
              </div>
              <div className="muted" style={{ marginTop: 10, textAlign: 'center' }}>
                이 링크는 로그인 없이 확인 가능합니다. (토큰 기반)
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
