"use client";
import Image from "next/image";
import { useEffect, useState } from "react";
import environment from "@/utils/environment";
import { GeneralStore } from "@/store/drawer.store";
import { Empty } from "antd";
export default function Andon() {
  const [timestamp, setTimestamp] = useState(Date.now());
  const image_path = GeneralStore((state) => state.image_path);

  useEffect(() => {
    const interval = setInterval(() => {
      setTimestamp(Date.now());
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <>
      {image_path !== null ? (
        <Image
          src={`${image_path}?refresh=${timestamp}`}
          loader={() => `${image_path}?refresh=${timestamp}`}
          alt={`Description of the image`}
          style={{ objectFit: "cover", width: "100%", height: "100%" }}
          width={1920}
          height={1080}
        />
      ) : (
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description={
            <p>
              ไม่พบรูป
              กรุณาคลิกที่ปุ่มด้านซ้ายเพื่อเลือกไลน์ที่ต้องการดูประสิทธิภาพ
            </p>
          }
        />
      )}
    </>
  );
}
