"use client";
import { GeneralStore } from "@/store/drawer.store";
import environment from "@/utils/environment";
import Image from "next/image";
import { useEffect, useState } from "react";

export default function AndonMain() {
  const [timestamp, setTimestamp] = useState(Date.now());
  const image_path = GeneralStore((state) => state.image_path);

  useEffect(() => {
    const interval = setInterval(() => {
      setTimestamp(Date.now());
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ width: "100%", height: "100%" }}>
      <Image
        src={`${image_path}/Andon/image/OA_Rotor_Assy_Line2.png?refresh=${timestamp}`}
        loader={() =>
          `${image_path}/Andon/image/OA_Rotor_Assy_Line2.png?refresh=${timestamp}`
        }
        alt={`Description of the image`}
        layout="fill"
        objectFit="contain"
      />
    </div>
  );
}
