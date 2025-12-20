import { useAuth } from '@clerk/nextjs';

export function useAdminToken() {
  const { isLoaded, isSignedIn, getToken, orgId, orgRole } = useAuth();

  const getAdminToken = async (): Promise<string> => {
    if (!isLoaded) throw new Error('Auth not loaded');
    if (!isSignedIn) throw new Error('Not signed in');

    const template = process.env.NEXT_PUBLIC_AUTH_TOKEN_TEMPLATE;
    const token = template ? await getToken({ template }) : await getToken();

    if (!token) throw new Error('No auth token');
    return token;
  };

  return { isLoaded, isSignedIn, orgId, orgRole, getAdminToken };
}
