package com.nishita.jobportal.controller;
import com.nishita.jobportal.dto.JobDtos.JobResponse;
import com.nishita.jobportal.service.JobService;
import com.nishita.jobportal.service.ExternalJobService;
import com.nishita.jobportal.dto.ExternalJobResponse;
import java.util.List;
import org.springframework.data.domain.Page;
import org.springframework.web.bind.annotation.*;
@RestController @RequestMapping("/api/jobs") public class JobController{
 private final JobService jobs; private final ExternalJobService externalJobs; public JobController(JobService j,ExternalJobService e){jobs=j;externalJobs=e;}
 @GetMapping Page<JobResponse> search(@RequestParam(defaultValue="") String q,@RequestParam(defaultValue="") String location,@RequestParam(defaultValue="0") int page,@RequestParam(defaultValue="12") int size,@RequestParam(defaultValue="createdAt") String sort){return jobs.search(q,location,page,size,sort);}
 @GetMapping("/{id}") JobResponse get(@PathVariable Long id){return jobs.get(id);}
 @GetMapping("/external/feed") List<ExternalJobResponse> external(@RequestParam(defaultValue="") String q,@RequestParam(defaultValue="") String location){return externalJobs.search(q,location);}
}
