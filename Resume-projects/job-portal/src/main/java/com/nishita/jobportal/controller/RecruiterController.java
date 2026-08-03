package com.nishita.jobportal.controller;
import com.nishita.jobportal.dto.ApplicationDtos.*;
import com.nishita.jobportal.dto.JobDtos.*;
import com.nishita.jobportal.dto.ProfileDtos.*;
import com.nishita.jobportal.entity.UserAccount;
import com.nishita.jobportal.service.*;
import jakarta.validation.Valid;
import org.springframework.data.domain.Page;
import org.springframework.http.*;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import java.util.*;
@RestController @RequestMapping("/api/recruiter") @PreAuthorize("hasRole('RECRUITER')") public class RecruiterController{
 private final CurrentUserService current;private final ProfileService profiles;private final JobService jobs;private final ApplicationService applications;private final AnalyticsService analytics;
 public RecruiterController(CurrentUserService c,ProfileService p,JobService j,ApplicationService a,AnalyticsService x){current=c;profiles=p;jobs=j;applications=a;analytics=x;}
 @PostMapping("/companies") ResponseEntity<CompanyResponse> company(@RequestBody CompanyRequest r,Authentication a){return ResponseEntity.status(201).body(profiles.createCompany(current.require(a),r));}
 @GetMapping("/companies") List<CompanyResponse> companies(Authentication a){return profiles.companies(current.require(a));}
 @PostMapping("/jobs") ResponseEntity<JobResponse> create(@Valid @RequestBody JobRequest r,Authentication a){return ResponseEntity.status(201).body(jobs.create(r,current.require(a)));}
 @PutMapping("/jobs/{id}") JobResponse update(@PathVariable Long id,@Valid @RequestBody JobRequest r,Authentication a){return jobs.update(id,r,current.require(a));}
 @PatchMapping("/jobs/{id}/close") JobResponse close(@PathVariable Long id,Authentication a){return jobs.close(id,current.require(a));}
 @GetMapping("/jobs") Page<JobResponse> jobs(@RequestParam(defaultValue="0")int page,@RequestParam(defaultValue="20")int size,Authentication a){return jobs.recruiterJobs(current.require(a),page,size);}
 @GetMapping("/applications") Page<ApplicationResponse> applications(@RequestParam(defaultValue="")String q,@RequestParam(required=false) com.nishita.jobportal.entity.ApplicationStatus status,@RequestParam(defaultValue="0")int page,@RequestParam(defaultValue="20")int size,Authentication a){return applications.recruiter(current.require(a),q,status,page,size);}
 @PatchMapping("/applications/{id}/status") ApplicationResponse status(@PathVariable Long id,@Valid @RequestBody StatusRequest r,Authentication a){return applications.updateStatus(id,r,current.require(a));}
 @GetMapping("/analytics") Map<String,Long> analytics(Authentication a){UserAccount u=current.require(a);return analytics.recruiter(u.getId());}
}
