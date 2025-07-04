import { useEffect, useState } from 'react';
import { getFirestore, collection, onSnapshot } from 'firebase/firestore';
import { app } from '../firebase'; // make sure this exports a valid Firebase app

const db = getFirestore(app);

export default function FileHistory() {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    const unsubscribe = onSnapshot(collection(db, 'filehistory'), (snapshot) => {
      const docs = snapshot.docs.map((doc) => ({
        id: doc.id,
        ...doc.data()
      }));
      setData(docs);
    });

    return () => unsubscribe();
  }, []);

  return (
    <div>
      <h2>FileHistory (Live Firebase Data)</h2>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}
