These are some ideas for future changes. Most are just ideas, since most are things I don't need. The logger is a weekend project, and might do more if something is annoying me.

### **Future changes** ###

- Start a new branch with influxdb 2

+ Allow solcast to provide conditions for the diverter
	+ If today's forecast doesn't expect enough sun, then some loads won't be activated (probably these loads would have a lower priority than the forecast).
		- You don't want to warm your pool, when there isn't enough sun.
		- On the other hand, you probably would like to provide any excess energy to your EV regardless of forecasts (running out of _gas_ is no fun). This could be either energy excess or by time (some users have lower rates during some hours of the day)

	+ Also have an option for when tomorrow's forecast is poor.
		- In that case, if today is good you probably want to heat your water heater to a higher temperature.
		- For instance, normally heat it to 60°C, but overheat it to 70-75°C if tomorrow will be poor. The regular 60°C would run if the forecast is good, however the other would only run when tomorrow isn't a good forecast.
			- This assumes you have two thermostats, or a way to change the set-point to a higher level with a logic signal

- Divert loads when the voltage rises too much.

- Allow seasonal control for the diverter
	- Disable a load during a season or a repeat date

+ Allow saved balance to provide conditions for the diverter
	+ Even if the forecast is poor, but there is enough of a balance to run the diverting load
	+ The required balance might be needed further down the year, so this complicates this. Specially if only a few months generate the year's saved balance

* Send data to PVoutput.org
	- Not a priority, but several people have asked about that

* Work with multiple inverters.
	- This is probably pretty low on the list, since it needs a major rewrite. Would have to call do_map through workers. The reason is to keep the total execution within 15-20s, in order to allow data updates every 30s.
