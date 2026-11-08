"use client";

import { useActionState } from "react";

import { Alert } from "@/components/atoms/alert";
import { Button } from "@/components/atoms/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/atoms/card";
import { Input } from "@/components/atoms/input";
import { Label } from "@/components/atoms/label";
import {
  createExampleRecordAction,
  type ICreateExampleRecordActionResult,
} from "@/features/example/actions/create-example-record.action";

const initialResult: ICreateExampleRecordActionResult = { isSuccess: false, message: "" };

export function ExampleForm(): React.ReactElement {
  const [result, formAction, isPending] = useActionState(createExampleRecordAction, initialResult);
  return (
    <Card>
      <CardHeader>
        <CardTitle>Removable example</CardTitle>
        <CardDescription>
          Creates a record through Server Action → controller → service → repository.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form action={formAction} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="example-title">Title</Label>
            <Input
              id="example-title"
              name="title"
              placeholder="A useful example"
              required
              minLength={3}
              maxLength={120}
            />
          </div>
          <Button disabled={isPending} type="submit">
            {isPending ? "Creating…" : "Create record"}
          </Button>
          {result.message ? (
            <Alert className={result.isSuccess ? "border-green-600" : "border-red-600"}>
              {result.message}
            </Alert>
          ) : null}
        </form>
      </CardContent>
    </Card>
  );
}
