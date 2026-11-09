"use client";

import { MapPin } from "lucide-react";

import { Alert } from "@/components/atoms/alert";
import { Label } from "@/components/atoms/label";
import { RadioGroup, RadioGroupItem } from "@/components/atoms/radio-group";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/atoms/select";
import type { Catalog, Profile } from "@/features/planner/model/types";
import { cn } from "@/lib/utils";

export function RegionSelector({
  profile,
  catalog,
  onChange,
}: {
  profile: Profile;
  catalog: Catalog;
  onChange: (profile: Profile) => void;
}) {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="profile-country">País (obrigatório)</Label>
        <Select
          value={profile.country}
          onValueChange={(country) => onChange({ ...profile, country, region: "" })}
        >
          <SelectTrigger id="profile-country">
            <SelectValue placeholder="Selecione seu país" />
          </SelectTrigger>
          <SelectContent>
            {catalog.countries.map((country) => (
              <SelectItem key={country.id} value={country.id}>
                {country.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      {profile.country === "Brasil" ? (
        <fieldset>
          <legend className="mb-4 font-semibold">Sua região no Brasil (obrigatório)</legend>
          <RadioGroup
            value={profile.region}
            onValueChange={(region) => onChange({ ...profile, region })}
            aria-label="Sua região no Brasil"
            className="sm:grid-cols-2"
          >
            {catalog.regions.map((region) => (
              <Label
                key={region.id}
                htmlFor={`region-${region.id}`}
                className={cn(
                  "bg-card has-focus-visible:ring-ring relative flex min-h-28 cursor-pointer items-start gap-3 rounded-2xl border border-[var(--border-control)] p-4 leading-relaxed has-focus-visible:ring-2",
                  profile.region === region.id && "border-[var(--herb)] bg-[var(--herb-soft)]",
                )}
              >
                <RadioGroupItem className="mt-0.5" id={`region-${region.id}`} value={region.id} />
                <span>
                  <span className="flex items-center gap-2 font-semibold">
                    <MapPin className="size-4" aria-hidden="true" />
                    {region.label}
                  </span>
                  {region.description && (
                    <span className="text-muted-foreground mt-2 block text-sm font-normal">
                      {region.description}
                    </span>
                  )}
                </span>
              </Label>
            ))}
          </RadioGroup>
        </fieldset>
      ) : profile.country ? (
        <Alert className="border-[var(--warning)] bg-[var(--warning-soft)] p-4 text-[var(--warning)]">
          <strong>Localidade sem cobertura demonstrativa.</strong>
          <p className="mt-2">
            O catálogo local cobre apenas as cinco regiões brasileiras. Selecione Brasil para
            explorar a demonstração. Nenhuma outra região será usada automaticamente.
          </p>
        </Alert>
      ) : (
        <p className="text-muted-foreground text-sm">
          Selecione um país para consultar a cobertura disponível.
        </p>
      )}
    </div>
  );
}
