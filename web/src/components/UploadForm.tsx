import { useEffect, useMemo, useRef, useState } from 'react';
import { uploadProof } from '../services/api';

interface UploadFormProps {
  token: string;
}

type UploadStatus = 'idle' | 'ready' | 'uploading' | 'success' | 'error';

const normalizeError = (msg: string) => {
  if (!msg) return '업로드에 실패했습니다. 다시 시도해주세요.';
  if (msg.includes('RATE_LIMITED')) return '요청이 너무 많습니다. 잠시 후 다시 시도해주세요.';
  if (msg.toLowerCase().includes('proof already uploaded')) return '이미 업로드 완료된 주문입니다.';
  return msg;
};

export const UploadForm = ({ token }: UploadFormProps) => {
  const [status, setStatus] = useState<UploadStatus>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const previewUrl = useMemo(() => {
    if (!file) return null;
    return URL.createObjectURL(file);
  }, [file]);

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const openCamera = () => fileInputRef.current?.click();

  const onFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const f = event.target.files?.[0];
    if (!f) return;
    setFile(f);
    setStatus('ready');
    setErrorMessage('');
  };

  const clear = () => {
    setFile(null);
    setStatus('idle');
    setErrorMessage('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const upload = async () => {
    if (!file) return;

    setStatus('uploading');
    setErrorMessage('');
    try {
      await uploadProof(token, file);
      setStatus('success');
      window.setTimeout(() => {
        window.location.href = `/p/${token}`;
      }, 650);
    } catch (e: any) {
      const msg = normalizeError(e?.message || String(e));
      setStatus('error');
      setErrorMessage(msg);
      // 이미 업로드된 경우는 확인 페이지로 바로 유도
      if (msg.includes('이미 업로드 완료')) {
        window.setTimeout(() => {
          window.location.href = `/p/${token}`;
        }, 650);
      }
    }
  };

  if (status === 'success') {
    return (
      <div className="ok">
        <div style={{ fontWeight: 700, marginBottom: 6 }}>업로드 완료</div>
        <div className="muted">확인 페이지로 이동합니다…</div>
        <div style={{ marginTop: 10 }}>
          <a className="btn secondary" href={`/p/${token}`}>확인 페이지 열기</a>
        </div>
      </div>
    );
  }

  return (
    <div className="stack">
      <input
        type="file"
        accept="image/*"
        capture="environment"
        onChange={onFileChange}
        ref={fileInputRef}
        style={{ display: 'none' }}
      />

      {previewUrl && (
        <div>
          <div className="label">미리보기</div>
          <img
            src={previewUrl}
            alt="preview"
            style={{ width: '100%', borderRadius: 16, border: '1px solid var(--line)' }}
          />
          <div className="muted" style={{ marginTop: 8 }}>
            파일: {file?.name} ({Math.round((file?.size || 0) / 1024)}KB)
          </div>
        </div>
      )}

      {!file && (
        <button className="btn" onClick={openCamera}>
          카메라 열기
        </button>
      )}

      {file && (
        <div className="row">
          <button className="btn" onClick={upload} disabled={status === 'uploading'}>
            {status === 'uploading' ? '업로드 중…' : '업로드'}
          </button>
          <button className="btn secondary" onClick={openCamera} disabled={status === 'uploading'}>
            다시 촬영
          </button>
          <button className="btn ghost" onClick={clear} disabled={status === 'uploading'}>
            초기화
          </button>
        </div>
      )}

      {status === 'error' && (
        <div className="danger">
          <div style={{ fontWeight: 700, marginBottom: 6 }}>업로드 실패</div>
          <div>{errorMessage}</div>
        </div>
      )}

      <div className="muted">
        팁: 화환 전체 + 리본 문구가 같이 보이도록 찍으면 CS가 줄어듭니다.
      </div>
    </div>
  );
};
