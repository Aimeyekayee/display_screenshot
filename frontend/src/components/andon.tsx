"use client";
import Image from "next/image";
import { useEffect, useState } from "react";
import environment from "@/utils/environment";
export default function Andon() {
  const [timestamp, setTimestamp] = useState(Date.now());

  useEffect(() => {
    const interval = setInterval(() => {
      setTimestamp(Date.now());
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <Image
      src={`${environment.IMAGE_SERVER}/Andon/image/OA_Rotor_Assy_Line2.png?refresh=${timestamp}`}
      loader={() =>
        `${environment.IMAGE_SERVER}/Andon/image/OA_Rotor_Assy_Line2.png?refresh=${timestamp}`
      }
      alt={`Description of the image`}
      style={{ objectFit: "cover", width: "100%", height: "100%" }}
      width={1920}
      height={1080}
    />
  );
}
