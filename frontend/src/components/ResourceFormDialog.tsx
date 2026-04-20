import React from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

export type FieldType = "text" | "number" | "date" | "select" | "checkbox";

export interface FieldSpec {
  name: string;
  label: string;
  type: FieldType;
  required?: boolean;
  placeholder?: string;
  options?: { value: string; label: string }[];
  defaultValue?: string | number | boolean;
}

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: string;
  fields: FieldSpec[];
  submitLabel?: string;
  onSubmit: (values: Record<string, any>) => Promise<unknown> | void;
}

// Single dialog used across pages for create-style forms. Data-driven: pass a
// field spec array and an onSubmit; no per-resource markup needed.
const ResourceFormDialog: React.FC<Props> = ({
  open,
  onOpenChange,
  title,
  description,
  fields,
  submitLabel = "Save",
  onSubmit,
}) => {
  const initial = React.useMemo(
    () =>
      fields.reduce<Record<string, any>>((acc, f) => {
        acc[f.name] =
          f.defaultValue ??
          (f.type === "checkbox" ? false : f.type === "number" ? "" : "");
        return acc;
      }, {}),
    [fields],
  );

  const [values, setValues] = React.useState<Record<string, any>>(initial);
  const [submitting, setSubmitting] = React.useState(false);

  React.useEffect(() => {
    if (open) setValues(initial);
  }, [open, initial]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const payload: Record<string, any> = {};
      for (const f of fields) {
        const v = values[f.name];
        if (v === "" || v === undefined || v === null) {
          if (f.required) {
            toast.error(`${f.label} is required`);
            setSubmitting(false);
            return;
          }
          continue;
        }
        payload[f.name] = f.type === "number" ? Number(v) : v;
      }
      await onSubmit(payload);
      onOpenChange(false);
    } catch (err: any) {
      toast.error(err?.message || "Failed to submit");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          {description && <DialogDescription>{description}</DialogDescription>}
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-3">
          {fields.map((f) => (
            <div key={f.name} className="flex flex-col gap-1.5">
              <Label htmlFor={f.name}>
                {f.label}
                {f.required && <span className="text-destructive"> *</span>}
              </Label>
              {f.type === "select" ? (
                <select
                  id={f.name}
                  className="h-8 rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring"
                  value={values[f.name] ?? ""}
                  onChange={(e) =>
                    setValues((v) => ({ ...v, [f.name]: e.target.value }))
                  }
                >
                  <option value="">— select —</option>
                  {f.options?.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
              ) : f.type === "checkbox" ? (
                <input
                  id={f.name}
                  type="checkbox"
                  checked={!!values[f.name]}
                  onChange={(e) =>
                    setValues((v) => ({ ...v, [f.name]: e.target.checked }))
                  }
                  className="h-4 w-4"
                />
              ) : (
                <Input
                  id={f.name}
                  type={f.type}
                  placeholder={f.placeholder}
                  value={values[f.name] ?? ""}
                  onChange={(e) =>
                    setValues((v) => ({ ...v, [f.name]: e.target.value }))
                  }
                />
              )}
            </div>
          ))}
          <DialogFooter className="pt-2">
            <DialogClose render={<Button type="button" variant="outline" />}>
              Cancel
            </DialogClose>
            <Button
              type="submit"
              disabled={submitting}
              className="bg-emerald-500 hover:bg-emerald-600 text-white"
            >
              {submitting ? "Saving…" : submitLabel}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default ResourceFormDialog;
