// Modals.tsx
import TemplatesModal from "@/modals/templatesModal";

interface ModalsProps {
  openModal: boolean;
  setOpenModal: (value: boolean) => void;
}

const ModalsComponent = ({
  openModal = false,
  setOpenModal = () => {},
}: ModalsProps) => (
  <>
    {openModal && <TemplatesModal open={openModal} setOpen={setOpenModal} />}
  </>
);

export default ModalsComponent;
