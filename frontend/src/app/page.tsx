"use client";
import environment from "@/utils/environment";
import { Carousel, ConfigProvider } from "antd";
import Image from "next/image";
import { useEffect, useState } from "react";
import Andon from "../components/andon";
import AlarmPareto from "../components/alarm.pareto";
import Setup from "../components/setup";

export default function Home() {
  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        padding: "1.5rem 1.5rem 1.5rem 1.5rem",
      }}
    >
      <ConfigProvider
        theme={{
          components: {
            Carousel: {
              arrowSize: 36,
              dotActiveWidth: 40,
              sizePopupArrow: 40,
            },
          },
        }}
      >
        <Carousel
          arrows
          infinite={false}
          autoplay
          style={{ height: "auto", width: "100%", border: "1px solid" }}
        >
          <div style={{ width: "100%", height: "100%" }}>
            <AlarmPareto />
          </div>
          <div style={{ width: "100%", height: "100%" }}>
            <Andon />
          </div>
          <div style={{ width: "100%", height: "100%" }}>
            <Setup />
          </div>
        </Carousel>
      </ConfigProvider>
    </div>
  );
}
