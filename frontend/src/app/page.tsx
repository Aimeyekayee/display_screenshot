"use client";
import environment from "@/utils/environment";
import Image from "next/image";
import { useEffect, useState } from "react";

export default function Home() {
  const [timestamp, setTimestamp] = useState(Date.now());

  useEffect(() => {
    const interval = setInterval(() => {
      setTimestamp(Date.now());
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ width: "100%", height: "100%" }}>
      <Image
        src={`${environment.IMAGE_SERVER}/Andon/OA_Rotor_Assy_Line2.png?refresh=${timestamp}`}
        loader={() =>
          `${environment.IMAGE_SERVER}/Andon/OA_Rotor_Assy_Line2.png?refresh=${timestamp}`
        }
        alt={`Description of the image`}
        layout="fill"
        objectFit="contain"
      />
    </div>
  );
}
