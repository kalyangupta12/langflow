import type {
  ColDef,
  RowClickedEvent,
  SelectionChangedEvent,
  ValueFormatterParams,
} from "ag-grid-community";
import { useRef, useState } from "react";

import Dropdown from "@/components/core/dropdownComponent";
import GlobalVariableModal from "@/components/core/GlobalVariableModal/GlobalVariableModal";
import TableComponent from "@/components/core/parameterRenderComponent/components/tableComponent";
import {
  useDeleteGlobalVariables,
  useGetGlobalVariables,
} from "@/controllers/API/queries/variables";
import type { GlobalVariable } from "@/types/global_variables";
import IconComponent, {
  ForwardedIconComponent,
} from "../../../../components/common/genericIconComponent";
import { Badge } from "../../../../components/ui/badge";
import { Button } from "../../../../components/ui/button";
import useAlertStore from "../../../../stores/alertStore";

export default function GlobalVariablesPage() {
  const setErrorData = useAlertStore((state) => state.setErrorData);
  const [openModal, setOpenModal] = useState(false);
  const initialData = useRef<GlobalVariable | undefined>(undefined);
  const BadgeRenderer = (props) => {
    return props.value !== "" ? (
      <div>
        <Badge variant="outline" size="md" className="font-normal">
          {props.value}
        </Badge>
      </div>
    ) : (
      <div></div>
    );
  };

  const DropdownEditor = ({ options, value, onValueChange }) => {
    return (
      <Dropdown options={options} value={value} onSelect={onValueChange}>
        <div className="-mt-1.5 w-full"></div>
      </Dropdown>
    );
  };
  // Column Definitions: Defines the columns to be displayed.
  const colDefs: ColDef[] = [
    {
      headerName: "Variable",
      field: "name",
      flex: 3,
      minWidth: 200,
      checkboxSelection: true,
      headerCheckboxSelection: true,
    },
    {
      headerName: "Type",
      field: "type",
      cellRenderer: BadgeRenderer,
      cellEditor: DropdownEditor,
      cellEditorParams: {
        options: ["Generic", "Credential"],
      },
      flex: 2,
      minWidth: 120,
    },
    {
      headerName: "Value",
      field: "value",
      flex: 3,
      minWidth: 150,
      valueFormatter: (params: ValueFormatterParams<GlobalVariable>) => {
        const isCreditential = params.data?.type === "Credential";

        if (isCreditential) {
          return "*****";
        }
        return params.value ?? "";
      },
    },
    {
      headerName: "Apply To Fields",
      field: "default_fields",
      valueFormatter: (params) => {
        return params.value?.join(", ") ?? "";
      },
      flex: 2,
      minWidth: 150,
      resizable: true,
    },
  ];

  const [selectedRows, setSelectedRows] = useState<string[]>([]);

  const { data: globalVariables } = useGetGlobalVariables();
  const { mutate: mutateDeleteGlobalVariable } = useDeleteGlobalVariables();

  async function removeVariables() {
    selectedRows.map(async (row) => {
      const id = globalVariables?.find((variable) => variable.name === row)?.id;
      mutateDeleteGlobalVariable(
        { id },
        {
          onError: () => {
            setErrorData({
              title: `Error deleting variable`,
              list: [`ID not found for variable: ${row}`],
            });
          },
        },
      );
    });
  }

  function updateVariables(event: RowClickedEvent<GlobalVariable>) {
    initialData.current = event.data;
    setOpenModal(true);
  }

  return (
    <div className="flex w-full flex-col gap-6 ">
      <div className="flex w-full items-start justify-between gap-6">
        <div className="flex w-full flex-col">
          <h2
            className="flex items-center text-lg font-semibold tracking-tight"
            data-testid="settings_menu_header"
          >
            Global Variables
            <ForwardedIconComponent
              name="Globe"
              className="ml-2 h-5 w-5 text-primary"
            />
          </h2>
          <p className="text-sm text-muted-foreground">
            Manage global variables and assign them to fields.
          </p>
        </div>
        <div className="flex flex-shrink-0 items-center gap-2">
          <GlobalVariableModal asChild>
            <Button data-testid="api-key-button-store" variant="primary">
              <IconComponent name="Plus" className="w-4" />
              Add New
            </Button>
          </GlobalVariableModal>
        </div>
      </div>

<div className="flex w-full h-[500px] overflow-hidden">
        <TableComponent
          key={"globalVariables"}
          overlayNoRowsTemplate="No data available"
          onSelectionChanged={(event: SelectionChangedEvent) => {
            setSelectedRows(event.api.getSelectedRows().map((row) => row.name));
          }}
          rowSelection="multiple"
          onRowClicked={updateVariables}
          suppressRowClickSelection={true}
          pagination={true}
          columnDefs={colDefs}
          rowData={globalVariables ?? []}
          onDelete={removeVariables}
        />
        {initialData.current && (
          <GlobalVariableModal
            key={initialData.current.id}
            initialData={initialData.current}
            open={openModal}
            setOpen={setOpenModal}
          />
        )}
      </div>
    </div>
  );
}
