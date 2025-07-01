import { useEffect, useState } from 'react';
import { collection, getFirestore, onSnapshot, DocumentData } from 'firebase/firestore';
import { app } from '../firebaseConfig';

const db = getFirestore(app);

export default function Reports() {
  const [data, setData] = useState<DocumentData[]>([]);

  useEffect(() => {
    const unsubscribe = onSnapshot(collection(db, 'reports'), snapshot => {
      const docs = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setData(docs);
    });
    return () => unsubscribe();
  }, []);

  return (
    <div>
      <h2>Reports (Live Firebase Data)</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
