import { useEffect, useState } from 'react';
import { db } from '../firebase';
import { collection, onSnapshot } from 'firebase/firestore';

export default function Admin() {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    const adminRef = collection(db, 'admin');
    const unsubscribe = onSnapshot(adminRef, (snapshot) => {
      const docs = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setData(docs);
    });
    return () => unsubscribe();
  }, []);

  return (
    <div>
      <h2>Admin (Live Firebase Data)</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
