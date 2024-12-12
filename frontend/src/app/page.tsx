"use client";
import environment from "@/utils/environment";
import { Carousel, ConfigProvider } from "antd";
import Image from "next/image";
import { useEffect, useState } from "react";
import Andon from "../components/andon";
import DrawerForm from "@/components/drawer";

export default function Home() {
  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        padding: "1.5rem 1.5rem 1.5rem 1.5rem",
      }}
    >
      <div style={{ width: "100%", height: "100%" }}>
        <Andon />
      </div>
      <DrawerForm />
    </div>
  );
}
