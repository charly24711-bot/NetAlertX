@echo off
title MONITOR ADMINISTRACION Y CAJAS - QUALICLASS (UPMS CDE)
color 0B
mode con: cols=115 lines=34

echo ===================================================================================================
echo    MONITOREO CONTINUO DE ESTABILIDAD: ADMIN, CAJAS Y FINANZAS - QUALICLASS (UPMS CDE)
echo ===================================================================================================
echo  Vigilando:
echo    - Servidor Qualiclass (192.168.3.99)
echo    - Admin / Caja 1       (192.168.3.39)
echo    - Caja 2               (192.168.3.23)
echo    - Administracion 2     (192.168.3.84)
echo    - Finanzas             (192.168.3.24)
echo    - MikroTik Core GW     (192.168.3.1)
echo.
echo  Registro guardandose automaticamente en logs diarios:
echo  monitor_admin_qualiclass_YYYY-MM-DD.log
echo ===================================================================================================
echo.

cd /d "c:\ENTORNO LOCAL\NetAlertX"
python monitor_admin_qualiclass.py

pause
