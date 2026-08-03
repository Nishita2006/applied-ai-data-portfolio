package com.nishita.jobportal.service;
import com.nishita.jobportal.dto.JobDtos.*;
import com.nishita.jobportal.entity.*;
import com.nishita.jobportal.exception.NotFoundException;
import com.nishita.jobportal.repository.*;
import org.springframework.data.domain.*;
import org.springframework.stereotype.Service;
@Service public class JobService{
 private final JobRepository jobs; private final CompanyRepository companies;
 public JobService(JobRepository j,CompanyRepository c){jobs=j;companies=c;}
 public Page<JobResponse> search(String q,String location,int page,int size,String sort){Pageable p=PageRequest.of(page,Math.min(size,50),Sort.by(sort).descending());return jobs.search(clean(q),clean(location),JobStatus.OPEN,p).map(JobResponse::from);}
 public JobResponse get(Long id){return JobResponse.from(find(id));}
 public JobResponse create(JobRequest r,UserAccount recruiter){Company c=companies.findById(r.companyId()).filter(x->x.getRecruiter().getId().equals(recruiter.getId())).orElseThrow(()->new NotFoundException("Company not found"));JobPosting j=new JobPosting();apply(j,r);j.setCompany(c);return JobResponse.from(jobs.save(j));}
 public JobResponse update(Long id,JobRequest r,UserAccount recruiter){JobPosting j=owned(id,recruiter);apply(j,r);return JobResponse.from(jobs.save(j));}
 public JobResponse close(Long id,UserAccount recruiter){JobPosting j=owned(id,recruiter);j.setStatus(JobStatus.CLOSED);return JobResponse.from(jobs.save(j));}
 public Page<JobResponse> recruiterJobs(UserAccount u,int page,int size){return jobs.findByCompanyRecruiterId(u.getId(),PageRequest.of(page,Math.min(size,50),Sort.by("createdAt").descending())).map(JobResponse::from);}
 private JobPosting owned(Long id,UserAccount u){return jobs.findById(id).filter(j->j.getCompany().getRecruiter().getId().equals(u.getId())).orElseThrow(()->new NotFoundException("Job not found"));}
 private JobPosting find(Long id){return jobs.findById(id).orElseThrow(()->new NotFoundException("Job not found"));}
 private void apply(JobPosting j,JobRequest r){if(r.salaryMin()!=null&&r.salaryMax()!=null&&r.salaryMin()>r.salaryMax())throw new IllegalArgumentException("Minimum salary cannot exceed maximum salary");j.setTitle(r.title());j.setDescription(r.description());j.setLocation(r.location());j.setEmploymentType(r.employmentType());j.setSkills(r.skills());j.setSalaryMin(r.salaryMin());j.setSalaryMax(r.salaryMax());}
 private String clean(String v){return v==null?"":v.trim();}
}
