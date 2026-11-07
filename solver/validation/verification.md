# Fluent local verification

Verified at 2026-11-07 18:49 Europe/London.

- Product: ANSYS Fluent 2022 R2, release 22.2.0, build 10212, built 2022-05-27.
- Executable: `D:\ANSYS Inc\v222\fluent\ntbin\win64\fluent.exe`
- License environment: `ANSYSLMD_LICENSE_FILE=1055@localhost`
- FlexNet status: localhost server and ansyslmd UP; see `license-status.txt`.
- Actual solver launch connected to this server and reported a license enabling four-way parallel execution.
- Native journal verified: `verify.jou` printed `MMME3086_JOURNAL_INTERFACE_OK` and exited with status 0.
- Successful command (requires execution outside the restricted sandbox for local license context):
  `& 'D:\ANSYS Inc\v222\fluent\ntbin\win64\fluent.exe' 2ddp -g -t1 -i verify.jou`
- Successful evidence: `launch-native.log`, `validation.transcript`, and `fluent-20261107-184849-21800.trn`.
- Default Python is Python 3.13 at `C:\Program Files\Python313\python.exe`; `ansys.fluent.core` is absent. Native Journal is the validated interface; PyFluent was not installed or claimed validated.
- Initial restricted-sandbox launch failed with `Cannot initialize ANSYS Licensing context`; its logs are retained separately as `launch.log` and `fluent-20261107-184750-5488.trn`. `fluent-999999-error.log` belongs to that failed attempt.
- An initial journal write used a wrong relative path and did not create the file; corrected before the successful verification.

No coursework case, mesh, physical properties, turbulence parameters, or solution has been fabricated. A mesh/case and assignment are still required for Task A.
