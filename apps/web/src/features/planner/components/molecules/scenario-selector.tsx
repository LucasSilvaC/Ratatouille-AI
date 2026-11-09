"use client";
import { Label } from "@/components/atoms/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/atoms/select";
import type { Scenario } from "@/features/planner/model/types";

export function ScenarioSelector({
  value,
  onChange,
  disabled = false,
}: {
  value: Scenario;
  onChange: (value: Scenario) => void;
  disabled?: boolean;
}) {
  return (
    <details className="scenario-panel">
      <summary>Cenários da demonstração</summary>
      <div className="mt-3 max-w-sm space-y-2">
        <Label htmlFor="cenario">Resultado da próxima operação</Label>
        <Select
          value={value}
          onValueChange={(next) => onChange(next as Scenario)}
          disabled={disabled}
        >
          <SelectTrigger id="cenario">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="success">Sucesso</SelectItem>
            <SelectItem value="error">Erro</SelectItem>
            <SelectItem value="empty">Sem candidatos</SelectItem>
            <SelectItem value="conflict">Conflito de versão</SelectItem>
          </SelectContent>
        </Select>
        <p className="text-muted-foreground text-sm">
          Simulação determinística. Para tentar novamente, selecione Sucesso.
        </p>
      </div>
    </details>
  );
}
