"use client";

import { Checkbox } from "@/components/atoms/checkbox";
import { Input } from "@/components/atoms/input";
import { Label } from "@/components/atoms/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/atoms/select";
import type { Catalog, Profile } from "@/features/planner/model/types";

interface ProfileFieldsProps {
  profile: Profile;
  catalog: Catalog;
  errors: Record<string, string>;
  onChange: (profile: Profile) => void;
}
export function ProfileFields({ profile, catalog, errors, onChange }: ProfileFieldsProps) {
  return (
    <div className="space-y-8">
      <section className="space-y-6" aria-labelledby="profile-basics">
        <div>
          <h2 id="profile-basics" className="text-2xl font-semibold">
            O básico, sem complicar.
          </h2>
          <p className="text-muted-foreground mt-2 text-sm">
            Use apenas informações fictícias nesta demonstração. Os campos opcionais não geram
            diagnósticos.
          </p>
        </div>
        <div className="space-y-2">
          <Label htmlFor="profile-name">Nome (obrigatório)</Label>
          <Input
            id="profile-name"
            name="name"
            autoComplete="off"
            maxLength={80}
            required
            value={profile.name}
            onChange={(event) => onChange({ ...profile, name: event.target.value })}
            placeholder="Como você prefere ser chamado?"
            aria-invalid={Boolean(errors.name)}
            aria-describedby="profile-name-hint profile-name-error"
          />
          <p id="profile-name-hint" className="text-muted-foreground text-sm">
            Usado para identificar seu perfil demonstrativo.
          </p>
          {errors.name && (
            <p id="profile-name-error" className="text-sm text-[var(--danger)]">
              {errors.name}
            </p>
          )}
        </div>
        <div className="grid gap-6 sm:grid-cols-2">
          {(
            [
              {
                key: "height",
                label: "Altura (cm)",
                hint: "Opcional. Informe a altura em centímetros.",
                placeholder: "Ex.: 168",
              },
              {
                key: "weight",
                label: "Peso (kg)",
                hint: "Opcional. Informe o peso em quilogramas.",
                placeholder: "Ex.: 64",
              },
            ] as const
          ).map((field) => (
            <div className="space-y-2" key={field.key}>
              <Label htmlFor={`profile-${field.key}`}>{field.label}</Label>
              <Input
                id={`profile-${field.key}`}
                inputMode="decimal"
                value={profile[field.key]}
                onChange={(event) => onChange({ ...profile, [field.key]: event.target.value })}
                placeholder={field.placeholder}
                aria-invalid={Boolean(errors[field.key])}
                aria-describedby={`profile-${field.key}-hint profile-${field.key}-error`}
              />
              <p id={`profile-${field.key}-hint`} className="text-muted-foreground text-sm">
                {field.hint}
              </p>
              {errors[field.key] && (
                <p id={`profile-${field.key}-error`} className="text-sm text-[var(--danger)]">
                  {errors[field.key]}
                </p>
              )}
            </div>
          ))}
        </div>
        <div className="space-y-2">
          <Label htmlFor="profile-gender">Gênero (opcional)</Label>
          <Select
            value={profile.gender}
            onValueChange={(gender) => onChange({ ...profile, gender })}
          >
            <SelectTrigger id="profile-gender" aria-describedby="profile-gender-hint">
              <SelectValue placeholder="Prefiro não informar" />
            </SelectTrigger>
            <SelectContent>
              {["Feminino", "Masculino", "Não-binário", "Prefiro não informar"].map((value) => (
                <SelectItem key={value} value={value}>
                  {value}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <p id="profile-gender-hint" className="text-muted-foreground text-sm">
            Dado opcional do protótipo; não altera as sugestões nesta demonstração.
          </p>
        </div>
      </section>
      <section className="space-y-6" aria-labelledby="profile-restrictions">
        <div>
          <h2 id="profile-restrictions" className="text-2xl font-semibold">
            O que precisamos considerar?
          </h2>
          <p className="text-muted-foreground mt-2 text-sm">
            Restrições têm prioridade sobre preferências. A demonstração não substitui orientação
            profissional nem valida alergênicos.
          </p>
        </div>
        {catalog.restrictions.map((group) => (
          <fieldset key={group.id} className="space-y-3 rounded-2xl border p-4">
            <legend className="px-1 font-semibold">{group.label}</legend>
            <p className="text-muted-foreground text-sm">{group.description}</p>
            <div className="grid gap-2 sm:grid-cols-2">
              {group.choices.map((choice) => (
                <Label
                  key={choice.id}
                  htmlFor={`restriction-${choice.id}`}
                  className="hover:bg-muted flex min-h-11 cursor-pointer items-center gap-3 rounded-xl p-2 leading-relaxed"
                >
                  <Checkbox
                    id={`restriction-${choice.id}`}
                    checked={profile.restrictions.includes(choice.id)}
                    onCheckedChange={(checked) =>
                      onChange({
                        ...profile,
                        restrictions: checked
                          ? [...profile.restrictions, choice.id]
                          : profile.restrictions.filter((id) => id !== choice.id),
                      })
                    }
                  />
                  {choice.label}
                </Label>
              ))}
            </div>
          </fieldset>
        ))}
        <div className="bg-muted rounded-xl p-4">
          <Label
            htmlFor="restrictions-reviewed"
            className="flex min-h-11 cursor-pointer items-start gap-3 leading-relaxed"
          >
            <Checkbox
              id="restrictions-reviewed"
              required
              className="mt-0.5"
              checked={profile.restrictionsReviewed}
              onCheckedChange={(checked) =>
                onChange({ ...profile, restrictionsReviewed: checked === true })
              }
              aria-invalid={Boolean(errors.restrictionsReviewed)}
              aria-describedby="restrictions-reviewed-hint restrictions-reviewed-error"
            />
            <span>
              Revisei os grupos e informei minhas restrições, ou não tenho restrições a informar.
              (obrigatório)
            </span>
          </Label>
          <p id="restrictions-reviewed-hint" className="text-muted-foreground mt-2 text-sm">
            Nenhuma opção é selecionada automaticamente.
          </p>
          {errors.restrictionsReviewed && (
            <p id="restrictions-reviewed-error" className="mt-2 text-sm text-[var(--danger)]">
              {errors.restrictionsReviewed}
            </p>
          )}
        </div>
      </section>
    </div>
  );
}
