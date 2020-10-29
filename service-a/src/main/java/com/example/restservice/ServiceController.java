package com.example.restservice;

import java.util.Date;
import java.util.concurrent.atomic.AtomicLong;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;



@RestController
public class ServiceController {
	
	boolean RUN = true;

	private static final String template = "Hello, %s!";
	private final AtomicLong counter = new AtomicLong();

	@GetMapping("/hello")
	public Hello hello(@RequestParam(value = "name", defaultValue = "Bitcoin") String name) {
		return new Hello(counter.incrementAndGet(), String.format(template, name));
	}
	
	@GetMapping("/start")
	public void startBitcoinCheck() {
			System.out.println("BitcoinPrice monitoring started. Printing in USD:");	
			BitcoinPrice bitcoinPrice = new BitcoinPrice();
			float bcprice = 0;
			float sum = 0;
			int count = 0;
			try {
		        while(RUN) {
		        	bcprice = bitcoinPrice.run();
		        	sum += bcprice;
		        	count ++;
		        	Thread.sleep(1*60*1000);
		        	//Thread.sleep(1*5*1000);
		        	if (count == 10) {
		        		System.out.println("Bitcoin average for 10 min: " + sum/count + "   USD   " + new Date());
		        		sum = 0;
		        		count = 0;
		        	}
		        }
	        } catch (Exception e) {
	            e.printStackTrace();
	        }
	}
	
}
