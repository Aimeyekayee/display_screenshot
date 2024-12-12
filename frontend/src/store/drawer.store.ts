import { StateCreator, create } from "zustand";

export interface IGeneralState {
  open: boolean;
  image_path: string|null;
  setImagePath: (image_path: string) => void;
  setOpen: (open: boolean) => void;
}

export const GeneralStore = create<IGeneralState>((...args) => {
  const [set, get] = args;
  return {
    open: false,
    image_path: null,
    setImagePath(image_path) {
      set({ image_path });
    },
    setOpen(open) {
      set({ open });
    },
  };
});
