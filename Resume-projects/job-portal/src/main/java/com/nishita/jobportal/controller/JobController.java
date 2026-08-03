package com.nishita.jobportal.controller;
import com.nishita.jobportal.dto.JobDtos.JobResponse;
import com.nishita.jobportal.service.JobService;
import org.springframework.data.domain.Page;
import org.springframework.web.bind.annotation.*;
@RestController @RequestMapping("/api/jobs") public class JobController{
 private final JobService jobs; public JobController(JobService j){jobs=j;}
 @GetMapping Page<JobResponse> search(@RequestParam(defaultValue="") String q,@RequestParam(defaultValue="") String location,@RequestParam(defaultValue="0") int page,@RequestParam(defaultValue="12") int size,@RequestParam(defaultValue="createdAt") String sort){return jobs.search(q,location,page,size,sort);}
 @GetMapping("/{id}") JobResponse get(@PathVariable Long id){return jobs.get(id);}
}
