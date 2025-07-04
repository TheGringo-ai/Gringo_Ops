// Auto-generated placeholder with Firebase logic
import { useEffect, useState } from 'react';
import { getFirestore, collection, onSnapshot } from 'firebase/firestore';
import { app } from '../firebaseConfig';

export default function Dashboard() {
  const [data, setData] = useState([]);

  useEffect(() => {
    const db = getFirestore(app);
    const unsubscribe = onSnapshot(collection(db, 'dashboard'), snapshot => {
      const docs = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setData(docs);
    });
    return () => unsubscribe();
  }, []);

  return (
    <div>
      <h2>Dashboard (Live Firebase Data)</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
