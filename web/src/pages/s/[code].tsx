import { GetServerSideProps } from 'next';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

export const getServerSideProps: GetServerSideProps = async (ctx) => {
  const code = (ctx.params?.code as string) || '';
  if (!code) return { notFound: true };

  try {
    const res = await fetch(`${API_BASE_URL}/public/s/${encodeURIComponent(code)}`);
    if (!res.ok) return { notFound: true };
    const data = (await res.json()) as { target_url?: string };

    if (!data?.target_url) return { notFound: true };

    return {
      redirect: {
        destination: data.target_url,
        permanent: false,
      },
    };
  } catch {
    return { notFound: true };
  }
};

export default function ShortRedirect() {
  return null;
}
