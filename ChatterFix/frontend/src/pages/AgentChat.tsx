import { useEffect, useState } from 'react';
import { collection, onSnapshot } from 'firebase/firestore';
import { db } from '../firebase';

export default function AgentChat() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const unsubscribe = onSnapshot(
      collection(db, 'agentchat'),
      (snapshot) => {
        const docs = snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() }));
        setData(docs);
        setLoading(false);
      },
      (err) => {
        console.error("Error fetching agentchat:", err);
        setError("Failed to load data.");
        setLoading(false);
      }
    );
    return () => unsubscribe();
  }, []);

  if (loading) return <div>Loading AgentChat...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>AgentChat (Live Firebase Data)</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
