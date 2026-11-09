"use client";

import { Checkbox } from "@/components/atoms/checkbox";
import { Label } from "@/components/atoms/label";
import type { Catalog, Profile } from "@/features/planner/model/types";
import { cn } from "@/lib/utils";

export function PreferenceSelector({
  profile,
  catalog,
  onChange,
  blockedReasons = {},
}: {
  profile: Profile;
  catalog: Catalog;
  onChange: (profile: Profile) => void;
  blockedReasons?: Record<string, string>;
}) {
  return (
    <div className="space-y-6">
      <p className="text-muted-foreground text-sm leading-relaxed">
        Opcional. Selecione quantas opções quiser. Não selecionar uma opção significa apenas que
        você não informou uma preferência.
      </p>
      {catalog.preferences.map((group) => (
        <fieldset className="space-y-3" key={group.id}>
          <legend className="mb-2 text-lg font-semibold">{group.label}</legend>
          <p className="text-muted-foreground text-sm">{group.description}</p>
          <div className="flex flex-wrap gap-3">
            {group.choices.map((choice) => (
              <div key={choice.id} className="max-w-full">
                <Label
                  htmlFor={`preference-${choice.id}`}
                  className={cn(
                    "bg-card flex min-h-12 max-w-full cursor-pointer items-center gap-2 rounded-full border border-[var(--border-control)] px-4 py-3 leading-relaxed",
                    profile.preferences.includes(choice.id) &&
                      !blockedReasons[choice.id] &&
                      "border-[var(--herb)] bg-[var(--herb-soft)] text-[var(--herb)]",
                    blockedReasons[choice.id] &&
                      "bg-muted text-muted-foreground cursor-not-allowed",
                  )}
                >
                  <Checkbox
                    id={`preference-${choice.id}`}
                    checked={profile.preferences.includes(choice.id) && !blockedReasons[choice.id]}
                    disabled={Boolean(blockedReasons[choice.id])}
                    aria-describedby={
                      blockedReasons[choice.id] ? `preference-${choice.id}-reason` : undefined
                    }
                    onCheckedChange={(checked) =>
                      onChange({
                        ...profile,
                        preferences: checked
                          ? [...profile.preferences, choice.id]
                          : profile.preferences.filter((id) => id !== choice.id),
                      })
                    }
                  />
                  {choice.label}
                </Label>
                {blockedReasons[choice.id] && (
                  <p
                    id={`preference-${choice.id}-reason`}
                    className="text-muted-foreground mt-2 max-w-64 text-sm"
                  >
                    {blockedReasons[choice.id]}
                  </p>
                )}
              </div>
            ))}
          </div>
        </fieldset>
      ))}
    </div>
  );
}
