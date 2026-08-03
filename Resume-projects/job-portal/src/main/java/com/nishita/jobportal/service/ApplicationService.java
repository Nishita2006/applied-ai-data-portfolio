package com.nishita.jobportal.service;
import com.nishita.jobportal.dto.ApplicationDtos.*;
import com.nishita.jobportal.entity.*;
import com.nishita.jobportal.exception.*;
import com.nishita.jobportal.repository.*;
import org.springframework.data.domain.*;
import org.springframework.stereotype.Service;
@Service public class ApplicationService{
 private final ApplicationRepository applications; private final JobRepository jobs;
 public ApplicationService(ApplicationRepository a,JobRepository j){applications=a;jobs=j;}
 public ApplicationResponse apply(ApplyRequest r,UserAccount candidate){JobPosting job=jobs.findById(r.jobId()).filter(j->j.getStatus()==JobStatus.OPEN).orElseThrow(()->new NotFoundException("Open job not found"));if(applications.existsByJobIdAndCandidateId(job.getId(),candidate.getId()))throw new ConflictException("You already applied for this job");JobApplication a=new JobApplication();a.setJob(job);a.setCandidate(candidate);a.setCoverNote(r.coverNote());return ApplicationResponse.from(applications.save(a));}
 public Page<ApplicationResponse> candidate(UserAccount u,int page,int size){return applications.findByCandidateId(u.getId(),PageRequest.of(page,Math.min(size,50),Sort.by("appliedAt").descending())).map(ApplicationResponse::from);}
 public Page<ApplicationResponse> recruiter(UserAccount u,String q,ApplicationStatus status,int page,int size){return applications.searchRecruiter(u.getId(),q==null?"":q.trim(),status,PageRequest.of(page,Math.min(size,50),Sort.by("appliedAt").descending())).map(ApplicationResponse::from);}
 public ApplicationResponse updateStatus(Long id,StatusRequest r,UserAccount recruiter){JobApplication a=applications.findById(id).filter(x->x.getJob().getCompany().getRecruiter().getId().equals(recruiter.getId())).orElseThrow(()->new NotFoundException("Application not found"));a.setStatus(r.status());return ApplicationResponse.from(applications.save(a));}
}
