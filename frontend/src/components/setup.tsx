"use client";
import environment from "@/utils/environment";
import Image from "next/image";
import { useEffect, useState } from "react";

export default function Setup() {
  const [timestamp, setTimestamp] = useState(Date.now());

  useEffect(() => {
    const interval = setInterval(() => {
      setTimestamp(Date.now());
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <Image
      src={`${environment.IMAGE_SERVER}/Andon/image/Setup_time_Rotor_Assy_Line2.png?refresh=${timestamp}`}
      loader={() =>
        `${environment.IMAGE_SERVER}/Andon/image/Setup_time_Rotor_Assy_Line2.png?refresh=${timestamp}`
      }
      style={{ objectFit: "cover" }}
      alt={`Description of the image`}
      width={1920}
      height={1080}
    />
  );
}
