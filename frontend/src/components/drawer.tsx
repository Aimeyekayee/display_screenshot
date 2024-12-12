import React, { useEffect, useState } from "react";
import { Button, Drawer, FloatButton, Form, Input, Select, Space } from "antd";
import axios from "axios";
import environment from "@/utils/environment";
import { GeneralStore } from "@/store/drawer.store";
import { FormOutlined } from "@ant-design/icons";

const { Option } = Select;

interface Line {
  line_id: number;
  line_fullname: string;
  image_path: string;
}

const DrawerForm: React.FC = () => {
  const [form] = Form.useForm();
  const [open, setOpen] = useState(false);
  const [lines, setLines] = useState<Line[]>([]);
  const setImagePath = GeneralStore((state) => state.setImagePath);
  const showDrawer = () => {
    setOpen(true);
  };
  const onClose = () => {
    setOpen(false);
  };

  const onFinish = (values: any) => {
    const image_path = values.image_path.split("split_here");
    setImagePath(image_path[1]);
  };

  const handleFetchLine = async () => {
    try {
      // const response = await axios.get(`${environment.IMAGE_SERVER}/get_line`);
      const response = await axios.get(`http://10.122.77.1:8012/get_line`);
      setLines(response.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    handleFetchLine();
  }, []);

  return (
    <>
      <FloatButton
        style={{ left: 20, top: 24, justifyContent: "flex-start" }}
        tooltip={<div>Change Line</div>}
        type="primary"
        icon={<FormOutlined />}
        onClick={showDrawer}
      >
        Open
      </FloatButton>
      <Drawer
        title="Select Line"
        onClose={onClose}
        open={open}
        placement="left"
      >
        <Form
          form={form}
          name="control-hooks"
          onFinish={onFinish}
          style={{ maxWidth: 600 }}
        >
          <Form.Item
            name="image_path"
            label="Line"
            rules={[{ required: true }]}
          >
            <Select
              placeholder="เลือกไลน์ที่ต้องการดูประสิทธิภาพ"
              showSearch
              allowClear
            >
              {lines.map((line) => (
                <Option
                  key={line.line_id}
                  value={line.line_fullname + `split_here` + line.image_path}
                >
                  {line.line_fullname}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            style={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
            }}
          >
            <Space>
              <Button type="primary" htmlType="submit">
                Load
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Drawer>
    </>
  );
};

export default DrawerForm;
