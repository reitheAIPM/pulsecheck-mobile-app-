## 🚦 Manual AI Scheduler Start (Post-Deploy)

After every Railway deploy, start the AI scheduler manually:

- **PowerShell:**
  ```powershell
  Invoke-WebRequest -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/start" -Method POST
  ```
- **Unix/macOS:**
  ```sh
  curl -X POST "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/start"
  ```

Check status:
```sh
curl -X GET "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/status"
``` 